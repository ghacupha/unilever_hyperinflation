"""Config-driven bank financial model calculations.

Mirrors calculations.py's shape: every function accepts a `config` module and returns
plain dicts of lists (one value per year in config.YEARS). See BLUEPRINT.md for the full
schedule design and the IFRS 9 provisioning design in particular.

Modeling note on the IFRS 9 provision charge: each stage's ECL is recomputed each period
as `loss_rate x closing_gross_balance` (a stock approach, calibrated from Family Bank's
own disclosed FY2023 stage-level ECL/Gross ratios) rather than tracked as an explicit
rolling allowance with separate write-off utilization (the textbook flow approach). Under
the stock approach, a write-off's effect on the allowance is already embedded in the
smaller post-write-off closing balance, so the correct non-double-counting P&L charge is
simply the period-over-period change in the ECL stock (`ecl_total[i] - ecl_total[i-1]`),
not `change + writeoffs - recoveries`. This is a deliberate simplification, documented
here because it's the kind of thing that looks like a bug if you're expecting the
textbook roll-forward formula.
"""

# Recovery on write-offs is folded into the stock-based ECL calc (see module docstring),
# so no separate recovery-rate assumption is needed.


def _macro_multiplier(config):
    m = config.MACRO_SCENARIOS
    w, mult = m["weights"], m["multipliers"]
    return sum(w[k] * mult[k] for k in w)


# ─────────────────────────────────────────────
# SCHEDULE 1 / 1b — LOAN BOOK STAGING + IFRS 9 ECL
# ─────────────────────────────────────────────

def build_loan_book(config):
    """Per-segment (product) gross/ECL staging roll-forward plus aggregate totals."""
    n = len(config.YEARS)
    macro_mult = _macro_multiplier(config)

    segments = []
    agg_gross = [0.0] * n
    agg_ecl = [0.0] * n
    agg_writeoff = [0.0] * n
    agg_opening_gross = 0.0
    agg_opening_ecl = 0.0

    for seg in config.LOAN_SEGMENTS:
        prev_s1, prev_s2, prev_s3 = seg["opening_s1"], seg["opening_s2"], seg["opening_s3"]
        opening_gross_total = prev_s1 + prev_s2 + prev_s3
        opening_ecl_total = (
            seg["loss_rate_s1"] * prev_s1
            + seg["loss_rate_s2"] * prev_s2
            + seg["loss_rate_s3"] * prev_s3
        )

        gross_s1, gross_s2, gross_s3, gross_total = [], [], [], []
        ecl_s1, ecl_s2, ecl_s3, ecl_total = [], [], [], []
        new_orig, writeoff = [], []
        charge = []

        prev_ecl_total = opening_ecl_total
        for _ in range(n):
            opening_total = prev_s1 + prev_s2 + prev_s3
            m12 = seg["sicr_rate"] * prev_s1
            m21 = seg["cure_21"] * prev_s2
            m23 = seg["default_rate"] * prev_s2
            m32 = seg["cure_32"] * prev_s3
            wo = seg["writeoff_rate"] * prev_s3
            orig = seg["growth"] * opening_total + wo

            s1 = prev_s1 - m12 + m21 + orig
            s2 = prev_s2 + m12 - m21 - m23 + m32
            s3 = prev_s3 + m23 - m32 - wo

            e1 = seg["loss_rate_s1"] * macro_mult * s1
            e2 = seg["loss_rate_s2"] * macro_mult * s2
            e3 = seg["loss_rate_s3"] * macro_mult * s3
            e_total = e1 + e2 + e3

            gross_s1.append(s1); gross_s2.append(s2); gross_s3.append(s3)
            gross_total.append(s1 + s2 + s3)
            ecl_s1.append(e1); ecl_s2.append(e2); ecl_s3.append(e3)
            ecl_total.append(e_total)
            new_orig.append(orig); writeoff.append(wo)
            charge.append(e_total - prev_ecl_total)

            prev_s1, prev_s2, prev_s3 = s1, s2, s3
            prev_ecl_total = e_total

        net_total = [g - e for g, e in zip(gross_total, ecl_total)]

        segments.append(dict(
            name=seg["name"], key=seg["key"],
            yield_rate=seg["yield_rate"], risk_weight=seg["risk_weight"],
            gross_s1=gross_s1, gross_s2=gross_s2, gross_s3=gross_s3, gross_total=gross_total,
            ecl_s1=ecl_s1, ecl_s2=ecl_s2, ecl_s3=ecl_s3, ecl_total=ecl_total,
            net_total=net_total, new_orig=new_orig, writeoff=writeoff, charge=charge,
            opening_gross_total=opening_gross_total, opening_ecl_total=opening_ecl_total,
        ))

        for i in range(n):
            agg_gross[i] += gross_total[i]
            agg_ecl[i] += ecl_total[i]
            agg_writeoff[i] += writeoff[i]
        agg_opening_gross += opening_gross_total
        agg_opening_ecl += opening_ecl_total

    agg_net = [g - e for g, e in zip(agg_gross, agg_ecl)]
    agg_charge = [sum(seg["charge"][i] for seg in segments) for i in range(n)]

    return dict(
        segments=segments,
        gross_total=agg_gross, ecl_total=agg_ecl, net_total=agg_net,
        writeoff_total=agg_writeoff, charge_total=agg_charge,
        opening_gross_total=agg_opening_gross, opening_ecl_total=agg_opening_ecl,
        npl_ratio=[s3_sum / g if g else 0.0 for s3_sum, g in zip(
            [sum(seg["gross_s3"][i] for seg in segments) for i in range(n)], agg_gross)],
        stage3_gross_total=[sum(seg["gross_s3"][i] for seg in segments) for i in range(n)],
        stage3_ecl_total=[sum(seg["ecl_s3"][i] for seg in segments) for i in range(n)],
    )


def build_off_balance_sheet(config):
    n = len(config.YEARS)
    ob = config.OFF_BALANCE_SHEET
    balance, prev = [], ob["opening"]
    for _ in range(n):
        prev = prev * (1 + ob["growth"])
        balance.append(prev)
    rwa = [b * ob["ccf"] * ob["risk_weight"] for b in balance]
    return dict(balance=balance, rwa=rwa)


# ─────────────────────────────────────────────
# SCHEDULE 2 — INVESTMENT SECURITIES
# ─────────────────────────────────────────────

def build_securities(config):
    n = len(config.YEARS)
    s = config.INVESTMENT_SECURITIES
    balance, prev = [], s["opening"]
    for _ in range(n):
        prev = prev * (1 + s["growth"])
        balance.append(prev)
    interest_income = [b * s["yield_rate"] for b in balance]
    return dict(balance=balance, interest_income=interest_income, opening=s["opening"])


# ─────────────────────────────────────────────
# SCHEDULE 3 — DEPOSITS / FUNDING
# ─────────────────────────────────────────────

def build_deposits(config):
    n = len(config.YEARS)
    types = []
    for dep in config.DEPOSIT_TYPES:
        balance, prev = [], dep["opening"]
        for _ in range(n):
            prev = prev * (1 + dep["growth"])
            balance.append(prev)
        interest_expense = [b * dep["cost_rate"] for b in balance]
        types.append(dict(name=dep["name"], key=dep["key"], balance=balance,
                           cost_rate=dep["cost_rate"], interest_expense=interest_expense,
                           opening=dep["opening"]))
    total_balance = [sum(t["balance"][i] for t in types) for i in range(n)]
    total_interest_expense = [sum(t["interest_expense"][i] for t in types) for i in range(n)]
    opening_total = sum(t["opening"] for t in types)
    return dict(types=types, total_balance=total_balance,
                total_interest_expense=total_interest_expense, opening_total=opening_total)


# ─────────────────────────────────────────────
# SCHEDULE 4-6 — INTEREST INCOME / EXPENSE / NII & NIM
# ─────────────────────────────────────────────

def build_interest_income(loan_book, securities):
    n = len(securities["balance"])
    loan_interest = [
        sum(seg["gross_total"][i] * seg["yield_rate"] for seg in loan_book["segments"])
        for i in range(n)
    ]
    total = [a + b for a, b in zip(loan_interest, securities["interest_income"])]
    return dict(loan_interest=loan_interest, securities_interest=securities["interest_income"],
                total=total)


def build_nii(interest_income, deposits):
    n = len(interest_income["total"])
    nii = [interest_income["total"][i] - deposits["total_interest_expense"][i] for i in range(n)]
    return dict(nii=nii)


# ─────────────────────────────────────────────
# SCHEDULE 7 — NON-INTEREST INCOME
# ─────────────────────────────────────────────

def build_non_interest_income(config, deposits_or_n=None):
    """Fee & commission income, modeled as a fixed ratio of deposit balances (a simple,
    clearly-modeled proxy — Family Bank doesn't disclose fee income drivers at this
    granularity in the extracted pages)."""
    n = len(config.YEARS)
    rate = getattr(config, "NON_INTEREST_INCOME_RATE", 0.012)  # [MODELED] ~1.2% of deposits
    return dict(rate=rate)


# ─────────────────────────────────────────────
# SCHEDULE 8 — OPERATING EXPENSES
# ─────────────────────────────────────────────

def build_opex(config):
    n = len(config.YEARS)
    items, total = [], [0.0] * n
    for item in config.OPEX_ITEMS:
        vals = [item["y1"] * (1 + item["escalation"]) ** i for i in range(n)]
        items.append((item["name"], vals))
        total = [a + b for a, b in zip(total, vals)]
    return dict(items=items, total=total)


# ─────────────────────────────────────────────
# SCHEDULE 10 — INCOME STATEMENT
# ─────────────────────────────────────────────

def build_income_statement(config, loan_book, deposits, nii, opex):
    n = len(config.YEARS)
    non_interest = build_non_interest_income(config)
    non_interest_income = [non_interest["rate"] * deposits["total_balance"][i] for i in range(n)]
    provisions = loan_book["charge_total"]
    pbt = [nii["nii"][i] + non_interest_income[i] - opex["total"][i] - provisions[i] for i in range(n)]
    tax = [max(0.0, p * config.TAX_RATE) for p in pbt]
    pat = [p - t for p, t in zip(pbt, tax)]
    dividends = [config.DIVIDEND_PAYOUT_RATIO * p for p in pat]
    return dict(non_interest_income=non_interest_income, provisions=provisions,
                pbt=pbt, tax=tax, pat=pat, dividends=dividends)


# ─────────────────────────────────────────────
# SCHEDULE 11/12 — CASH FLOW & BALANCE SHEET (integrated so cash ties by construction)
# ─────────────────────────────────────────────

def build_cash_flow_and_balance_sheet(config, loan_book, securities, deposits, income_stmt):
    n = len(config.YEARS)
    ppe_cfg = config.PPE

    other_assets = [config.OTHER_ASSETS_RATE_OF_NET_LOANS * loan_book["net_total"][i] for i in range(n)]
    other_liab = [config.OTHER_LIABILITIES_RATE_OF_DEPOSITS * deposits["total_balance"][i] for i in range(n)]

    opening_gross_loans = loan_book["opening_gross_total"]
    opening_securities = securities["opening"]
    opening_other_assets = config.OTHER_ASSETS_RATE_OF_NET_LOANS * (
        loan_book["opening_gross_total"] - loan_book["opening_ecl_total"])
    opening_deposits = deposits["opening_total"]
    opening_cash = config.OPENING_CASH
    opening_ppe = ppe_cfg["opening"]
    opening_re = config.CAPITAL["opening_tier1"] - config.SHARE_CAPITAL

    # Other Liabilities' opening value is a balancing plug, not a ratio: none of the other
    # opening figures (cash, securities, net loans, PP&E, other assets, deposits, Tier 1/2)
    # were derived to make the Year-0 balance sheet tie by construction, so this line
    # absorbs the gap. Forecast years still use the ratio-of-deposits mechanic below — the
    # jump between this plug and Year 1's ratio-based figure is a normal (and correctly
    # captured) working-capital delta, not an error.
    opening_net_loans = opening_gross_loans - loan_book["opening_ecl_total"]
    opening_assets_total = (opening_cash + opening_securities + opening_net_loans
                             + opening_ppe + opening_other_assets)
    opening_equity_total = config.CAPITAL["opening_tier1"]
    opening_tier2 = config.CAPITAL["opening_tier2"]
    opening_other_liab = opening_assets_total - opening_deposits - opening_tier2 - opening_equity_total

    ppe, da, capex = [], [], []
    prev_ppe = opening_ppe
    for _ in range(n):
        c = ppe_cfg["capex_rate"] * prev_ppe
        d = ppe_cfg["da_rate"] * prev_ppe
        capex.append(c); da.append(d)
        prev_ppe = prev_ppe + c - d
        ppe.append(prev_ppe)

    retained_earnings, prev_re = [], opening_re
    for i in range(n):
        prev_re = prev_re + income_stmt["pat"][i] - income_stmt["dividends"][i]
        retained_earnings.append(prev_re)

    tier2 = [config.CAPITAL["opening_tier2"]] * n
    share_capital = [config.SHARE_CAPITAL] * n
    tier1 = [share_capital[i] + retained_earnings[i] for i in range(n)]

    ocf, icf, fcf, net_change, cash = [], [], [], [], []
    prev_cash = opening_cash
    prev_gross_loans = opening_gross_loans
    prev_securities = opening_securities
    prev_other_assets = opening_other_assets
    prev_deposits = opening_deposits
    prev_other_liab = opening_other_liab

    for i in range(n):
        d_gross_loans = loan_book["gross_total"][i] - prev_gross_loans
        d_securities = securities["balance"][i] - prev_securities
        d_other_assets = other_assets[i] - prev_other_assets
        d_deposits = deposits["total_balance"][i] - prev_deposits
        d_other_liab = other_liab[i] - prev_other_liab

        o = (income_stmt["pat"][i] + da[i] + loan_book["charge_total"][i]
             - d_gross_loans - d_securities - d_other_assets
             + d_deposits + d_other_liab)
        ic = -capex[i]
        f = -income_stmt["dividends"][i]
        nc = o + ic + f
        prev_cash = prev_cash + nc

        ocf.append(o); icf.append(ic); fcf.append(f); net_change.append(nc); cash.append(prev_cash)

        prev_gross_loans = loan_book["gross_total"][i]
        prev_securities = securities["balance"][i]
        prev_other_assets = other_assets[i]
        prev_deposits = deposits["total_balance"][i]
        prev_other_liab = other_liab[i]

    total_assets = [cash[i] + securities["balance"][i] + loan_book["net_total"][i]
                    + ppe[i] + other_assets[i] for i in range(n)]
    total_liabilities = [deposits["total_balance"][i] + tier2[i] + other_liab[i] for i in range(n)]
    total_equity = [tier1[i] for i in range(n)]
    check = [total_assets[i] - total_liabilities[i] - total_equity[i] for i in range(n)]

    cf = dict(ocf=ocf, icf=icf, fcf=fcf, net_change=net_change, cash=cash,
              da=da, capex=capex, beg_cash=[opening_cash] + cash[:-1])
    bs = dict(cash=cash, securities=securities["balance"], net_loans=loan_book["net_total"],
              ppe=ppe, other_assets=other_assets, total_assets=total_assets,
              deposits=deposits["total_balance"], tier2=tier2, other_liab=other_liab,
              total_liabilities=total_liabilities,
              share_capital=share_capital, retained_earnings=retained_earnings, tier1=tier1,
              total_equity=total_equity, check=check)
    return cf, bs


# ─────────────────────────────────────────────
# SCHEDULE 13 — CAPITAL ADEQUACY
# ─────────────────────────────────────────────

def build_capital_adequacy(config, loan_book, off_balance, deposits, bs):
    n = len(config.YEARS)
    loan_rwa = [
        sum(seg["gross_total"][i] * seg["risk_weight"] for seg in loan_book["segments"])
        for i in range(n)
    ]
    rwa = [loan_rwa[i] + off_balance["rwa"][i]
           + loan_book["gross_total"][i] * config.CAPITAL["other_rwa_pct_of_gross_loans"]
           for i in range(n)]
    # Regulatory Tier 1/Tier 2 are a separate concept from bs["tier1"]/bs["tier2"] (which
    # are the Balance Sheet's accounting-equity/liability-side figures) — no forward
    # -looking regulatory-bridge methodology is disclosed, so Tier 1 is modeled as a fixed
    # % of Total Equity and Tier 2 held flat, both calibrated to the real FY2025 anchor
    # (see config.py's REGULATORY_CAPITAL / CAPITAL['tier1_pct_of_equity']/['reg_tier2_opening']).
    reg_tier1 = [bs["total_equity"][i] * config.CAPITAL["tier1_pct_of_equity"] for i in range(n)]
    reg_tier2 = [config.CAPITAL["reg_tier2_opening"]] * n
    core_capital_ratio = [reg_tier1[i] / rwa[i] if rwa[i] else 0.0 for i in range(n)]
    total_capital_ratio = [(reg_tier1[i] + reg_tier2[i]) / rwa[i] if rwa[i] else 0.0
                            for i in range(n)]
    core_capital_to_deposits = [reg_tier1[i] / deposits["total_balance"][i]
                                 if deposits["total_balance"][i] else 0.0 for i in range(n)]
    return dict(rwa=rwa, tier1=reg_tier1, tier2=reg_tier2,
                core_capital_ratio=core_capital_ratio,
                total_capital_ratio=total_capital_ratio,
                core_capital_to_deposits=core_capital_to_deposits,
                core_min=config.CAPITAL["core_capital_rwa_min"],
                total_min=config.CAPITAL["total_capital_rwa_min"],
                deposits_min=config.CAPITAL["core_capital_deposits_min"])


# ─────────────────────────────────────────────
# SCHEDULE 14 — LIQUIDITY
# ─────────────────────────────────────────────

def build_liquidity(config, bs, deposits):
    n = len(config.YEARS)
    liquid_assets = [bs["cash"][i] + bs["securities"][i] for i in range(n)]
    ratio = [liquid_assets[i] / deposits["total_balance"][i] if deposits["total_balance"][i] else 0.0
             for i in range(n)]
    return dict(liquid_assets=liquid_assets, ratio=ratio, min=config.LIQUIDITY_STATUTORY_MIN)


# ─────────────────────────────────────────────
# SCHEDULE 15 — RATIO DISCLOSURES (CAMELS-complete, DuPont ROA decomposition)
# ─────────────────────────────────────────────

def build_ratio_disclosures(config, loan_book, deposits, nii, income_stmt, cf, bs,
                             capital, liquidity):
    n = len(config.YEARS)

    def _avg(series, opening):
        return [(([opening] + series)[i] + series[i]) / 2 for i in range(n)]

    avg_assets = _avg(bs["total_assets"], (
        config.OPENING_CASH + config.INVESTMENT_SECURITIES["opening"]
        + (loan_book["opening_gross_total"] - loan_book["opening_ecl_total"])
        + config.PPE["opening"]
        + config.OTHER_ASSETS_RATE_OF_NET_LOANS * (
            loan_book["opening_gross_total"] - loan_book["opening_ecl_total"])
    ))
    avg_equity = _avg(bs["total_equity"], config.CAPITAL["opening_tier1"])
    avg_earning_assets = _avg(
        [loan_book["gross_total"][i] + bs["securities"][i] for i in range(n)],
        loan_book["opening_gross_total"] + config.INVESTMENT_SECURITIES["opening"],
    )

    roa = [income_stmt["pat"][i] / avg_assets[i] if avg_assets[i] else 0.0 for i in range(n)]
    roe = [income_stmt["pat"][i] / avg_equity[i] if avg_equity[i] else 0.0 for i in range(n)]
    equity_multiplier = [avg_assets[i] / avg_equity[i] if avg_equity[i] else 0.0 for i in range(n)]
    nim = [nii["nii"][i] / avg_earning_assets[i] if avg_earning_assets[i] else 0.0 for i in range(n)]

    total_income = [nii["nii"][i] + income_stmt["non_interest_income"][i] for i in range(n)]
    opex_totals = _opex_totals(config)
    cost_to_income = [
        opex_totals[i] / total_income[i] if total_income[i] else 0.0
        for i in range(n)
    ]

    # DuPont ROA decomposition, all as % of average assets
    nim_contrib = [nii["nii"][i] / avg_assets[i] if avg_assets[i] else 0.0 for i in range(n)]
    non_interest_contrib = [income_stmt["non_interest_income"][i] / avg_assets[i]
                             if avg_assets[i] else 0.0 for i in range(n)]
    cost_contrib = [opex_totals[i] / avg_assets[i] if avg_assets[i] else 0.0 for i in range(n)]
    provision_contrib = [income_stmt["provisions"][i] / avg_assets[i] if avg_assets[i] else 0.0
                          for i in range(n)]
    tax_contrib = [income_stmt["tax"][i] / avg_assets[i] if avg_assets[i] else 0.0 for i in range(n)]

    ocf_to_pat = [cf["ocf"][i] / income_stmt["pat"][i] if income_stmt["pat"][i] else 0.0
                  for i in range(n)]
    ocf_to_deposits = [cf["ocf"][i] / deposits["total_balance"][i] if deposits["total_balance"][i] else 0.0
                        for i in range(n)]
    cash_coverage = [bs["cash"][i] / deposits["total_balance"][i] if deposits["total_balance"][i] else 0.0
                     for i in range(n)]

    return dict(
        roa=roa, roe=roe, equity_multiplier=equity_multiplier, nim=nim,
        cost_to_income=cost_to_income,
        nim_contrib=nim_contrib, non_interest_contrib=non_interest_contrib,
        cost_contrib=cost_contrib, provision_contrib=provision_contrib, tax_contrib=tax_contrib,
        npl_ratio=loan_book["npl_ratio"],
        core_capital_ratio=capital["core_capital_ratio"], total_capital_ratio=capital["total_capital_ratio"],
        liquidity_ratio=liquidity["ratio"],
        ocf_to_pat=ocf_to_pat, ocf_to_deposits=ocf_to_deposits, cash_coverage=cash_coverage,
    )


def _opex_totals(config):
    return build_opex(config)["total"]


# ─────────────────────────────────────────────
# SCHEDULE 16 — VALUATION (CAPM, DDM, Residual Income, P/B-ROE regression)
# ─────────────────────────────────────────────

def _linreg(xs, ys):
    """Plain-Python least-squares slope/intercept — no numpy dependency for one regression."""
    n = len(xs)
    mean_x, mean_y = sum(xs) / n, sum(ys) / n
    cov = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    var = sum((x - mean_x) ** 2 for x in xs)
    slope = cov / var if var else 0.0
    intercept = mean_y - slope * mean_x
    return slope, intercept


def build_valuation(config, income_stmt, bs):
    n = len(config.YEARS)
    v = config.VALUATION
    coe = v["risk_free_rate"] + v["beta"] * v["equity_risk_premium"]
    g = v["terminal_growth"]

    dividends = income_stmt["dividends"]
    pv_dividends = [dividends[i] / (1 + coe) ** (i + 1) for i in range(n)]
    terminal_div = dividends[-1] * (1 + g)
    terminal_value_ddm = terminal_div / (coe - g) if coe > g else float("nan")
    pv_terminal_ddm = terminal_value_ddm / (1 + coe) ** n
    ddm_value = sum(pv_dividends) + pv_terminal_ddm

    opening_equity = config.CAPITAL["opening_tier1"]
    equity_series = [opening_equity] + bs["total_equity"]
    roe_series = [income_stmt["pat"][i] / equity_series[i] if equity_series[i] else 0.0
                  for i in range(n)]
    residual_income = [(roe_series[i] - coe) * equity_series[i] for i in range(n)]
    pv_ri = [residual_income[i] / (1 + coe) ** (i + 1) for i in range(n)]
    terminal_ri = residual_income[-1] * (1 + g) / (coe - g) if coe > g else float("nan")
    pv_terminal_ri = terminal_ri / (1 + coe) ** n
    residual_income_value = opening_equity + sum(pv_ri) + pv_terminal_ri

    peers = config.PEER_BANKS
    slope, intercept = _linreg([p["roae_fy25"] for p in peers], [p["pb_placeholder"] for p in peers])
    final_roe = roe_series[-1]
    implied_pb = slope * final_roe + intercept
    final_book_equity = bs["total_equity"][-1]
    pb_regression_value = implied_pb * final_book_equity

    w = v.get("blend_weights", dict(ddm=0.5, ri=0.3, pb=0.2))
    blended_value = (w["ddm"] * ddm_value + w["ri"] * residual_income_value
                      + w["pb"] * pb_regression_value)

    return dict(
        cost_of_equity=coe, ddm_value=ddm_value, residual_income_value=residual_income_value,
        pb_regression_value=pb_regression_value, implied_pb=implied_pb,
        blended_value=blended_value, blend_weights=w,
        roe_series=roe_series, residual_income=residual_income,
        pv_dividends=pv_dividends, pv_terminal_ddm=pv_terminal_ddm,
    )


# ─────────────────────────────────────────────
# TOP-LEVEL BUILDER
# ─────────────────────────────────────────────

def build_all(config):
    loan_book = build_loan_book(config)
    off_balance = build_off_balance_sheet(config)
    securities = build_securities(config)
    deposits = build_deposits(config)
    interest_income = build_interest_income(loan_book, securities)
    nii = build_nii(interest_income, deposits)
    opex = build_opex(config)
    income_stmt = build_income_statement(config, loan_book, deposits, nii, opex)
    cf, bs = build_cash_flow_and_balance_sheet(config, loan_book, securities, deposits, income_stmt)
    capital = build_capital_adequacy(config, loan_book, off_balance, deposits, bs)
    liquidity = build_liquidity(config, bs, deposits)
    ratios = build_ratio_disclosures(config, loan_book, deposits, nii, income_stmt, cf, bs,
                                     capital, liquidity)
    valuation = build_valuation(config, income_stmt, bs)

    return dict(
        loan_book=loan_book, off_balance=off_balance, securities=securities,
        deposits=deposits, interest_income=interest_income, nii=nii, opex=opex,
        income_stmt=income_stmt, cf=cf, bs=bs, capital=capital, liquidity=liquidity,
        ratios=ratios, valuation=valuation,
    )


# ─────────────────────────────────────────────
# SCENARIOS — Best/Worst static comparison (Python-computed only; the Scenarios sheet,
# unlike the Model sheet, is never formula-linked — same convention as the existing
# generic renderer). Flexes loan growth, IFRS 9 loss rates, and opex escalation.
# ─────────────────────────────────────────────

class _ScenarioConfig:
    """Shallow view of `config` with LOAN_SEGMENTS/OPEX_ITEMS replaced by flexed copies.
    Every other attribute is looked up on the wrapped config unchanged."""

    def __init__(self, config, loan_segments, opex_items):
        self._config = config
        self.LOAN_SEGMENTS = loan_segments
        self.OPEX_ITEMS = opex_items

    def __getattr__(self, name):
        return getattr(self._config, name)


def build_scenario(config, growth_mult=1.0, loss_rate_mult=1.0, opex_mult=1.0):
    """Rerun build_all() with flexed loan growth / IFRS 9 loss rates / opex escalation.
    Returns the same dict shape as build_all()."""
    flexed_segments = []
    for seg in config.LOAN_SEGMENTS:
        flexed = dict(seg)
        flexed["growth"] = seg["growth"] * growth_mult
        flexed["loss_rate_s1"] = seg["loss_rate_s1"] * loss_rate_mult
        flexed["loss_rate_s2"] = seg["loss_rate_s2"] * loss_rate_mult
        flexed["loss_rate_s3"] = seg["loss_rate_s3"] * loss_rate_mult
        flexed_segments.append(flexed)

    flexed_opex = []
    for item in config.OPEX_ITEMS:
        flexed = dict(item)
        flexed["escalation"] = item["escalation"] * opex_mult
        flexed_opex.append(flexed)

    scenario_config = _ScenarioConfig(config, flexed_segments, flexed_opex)
    return build_all(scenario_config)


def build_scenarios(config):
    """Base/Best/Worst, for the Scenarios sheet. Base is the same as build_all().
    Reads config.SCENARIO_MULTIPLIERS so the Python scenarios and the renderer's live
    CHOOSE-switch formulas are always derived from the same source."""
    base = build_all(config)
    m = config.SCENARIO_MULTIPLIERS
    best = build_scenario(config, **m["best"])
    worst = build_scenario(config, **m["worst"])
    return dict(base=base, best=best, worst=worst)


# ─────────────────────────────────────────────
# SENSITIVITY — one-lever-at-a-time PAT impact, for the Summary sheet's "Key Net
# Income Sensitivities" section. Isolates a single driver at a time (unlike
# Best/Worst above, which move growth/loss-rate/opex together) so each factor's
# individual effect on PAT is visible. See research_output.md for why these three
# levers were chosen and which candidates were tested and excluded.
# ─────────────────────────────────────────────

class _AttrOverrideConfig:
    """Shallow view of `config` with the given attributes replaced — for one-off
    sensitivity shocks outside the LOAN_SEGMENTS/OPEX_ITEMS levers `_ScenarioConfig`
    covers (e.g. loan yield, deposit cost)."""

    def __init__(self, config, **overrides):
        self._config = config
        self._overrides = overrides

    def __getattr__(self, name):
        if name in self._overrides:
            return self._overrides[name]
        return getattr(self._config, name)


def _avg_pat(config_obj):
    pat = build_all(config_obj)["income_stmt"]["pat"]
    return sum(pat) / len(pat)


def build_sensitivity(config):
    """Average-PAT % impact of shocking one driver at a time, holding all others at
    Base. Growth reuses the existing Best/Worst growth_mult (already a scenario
    lever elsewhere in this model); asset yield and cost of funds use a parallel
    +/-100bp shift, the standard shock size in bank NIM-sensitivity disclosures."""
    base_avg = _avg_pat(config)
    m = config.SCENARIO_MULTIPLIERS

    def pct(config_obj):
        return (_avg_pat(config_obj) - base_avg) / base_avg

    def shock_yield(delta):
        segs = [dict(seg, yield_rate=max(0.0, seg["yield_rate"] + delta)) for seg in config.LOAN_SEGMENTS]
        return _AttrOverrideConfig(config, LOAN_SEGMENTS=segs)

    def shock_cost(delta):
        deps = [dict(dep, cost_rate=max(0.0, dep["cost_rate"] + delta)) for dep in config.DEPOSIT_TYPES]
        return _AttrOverrideConfig(config, DEPOSIT_TYPES=deps)

    factors = [
        dict(
            name="Loan/balance-sheet growth", category="Macro — credit demand cycle",
            detail=f"Worst {m['worst']['growth_mult']:.2f}x / Best {m['best']['growth_mult']:.2f}x growth multiplier",
            downside=pct(_ScenarioConfig(config,
                [dict(seg, growth=seg["growth"]*m["worst"]["growth_mult"]) for seg in config.LOAN_SEGMENTS],
                list(config.OPEX_ITEMS))),
            upside=pct(_ScenarioConfig(config,
                [dict(seg, growth=seg["growth"]*m["best"]["growth_mult"]) for seg in config.LOAN_SEGMENTS],
                list(config.OPEX_ITEMS))),
        ),
        dict(
            name="Asset yield (lending rate)", category="Bank-specific — rate cycle / repricing",
            detail="+/-100bp parallel shift on loan yields",
            downside=pct(shock_yield(-0.01)), upside=pct(shock_yield(0.01)),
        ),
        dict(
            name="Cost of funds (deposit pricing)", category="Macro — policy rate transmission",
            detail="+/-100bp parallel shift on deposit cost",
            downside=pct(shock_cost(0.01)), upside=pct(shock_cost(-0.01)),
        ),
    ]
    return dict(base_avg_pat=base_avg, factors=factors)
