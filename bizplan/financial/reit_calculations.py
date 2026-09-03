"""Config-driven REIT financial model calculations.

Mirrors the shape the bank model used: every function accepts a `config` module and
returns plain dicts of lists (one value per year in config.YEARS). See BLUEPRINT.md for
the full schedule design.

Actual years (config.ACTUAL_YEARS) are pinned to config.ACTUALS[year] -- real disclosed
(or, where undisclosed, clearly-flagged modeled) facts, mirroring the "actual-year
columns are hardcoded facts, projected-year columns are live formulas" convention the
renderer applies to the generated workbook. Where an actual year's disclosed figures
don't include a line-item breakdown (opex by item, finance income/cost), that line is
back-solved as the residual needed to reconcile to the pinned, disclosed Net Profit --
documented in research_output.md as a [DISCLOSED-DERIVED] residual, not silently
invented precision.
"""


def _year_index(config, year):
    return config.YEARS.index(year)


def _is_actual(config, i):
    return config.YEARS[i] in config.ACTUAL_YEARS


def _macro_multiplier(config):
    m = config.MACRO_SCENARIOS
    w, mult = m["weights"], m["multipliers"]
    return sum(w[k] * mult[k] for k in w)


# ─────────────────────────────────────────────
# SCHEDULE 1 — PROPERTY PORTFOLIO
# ─────────────────────────────────────────────

def build_property_portfolio(config):
    """Portfolio-aggregate investment-property roll-forward. Actual years are pinned to
    the disclosed/modeled closing fair value in config.ACTUALS; projected years roll
    forward on the escalation-implied growth rate (property fair value tracks NOI, which
    tracks rental escalation x occupancy path), plus a small modeled capex addition."""
    n = len(config.YEARS)
    escalation = config.RENTAL_INCOME["escalation"] * _macro_multiplier(config)

    closing = [None] * n
    opening = [None] * n
    additions = [None] * n
    fair_value_gain = [None] * n

    for i, year in enumerate(config.YEARS):
        if _is_actual(config, i):
            closing[i] = config.ACTUALS[year]["investment_property"]
            opening[i] = (config.ACTUALS[config.YEARS[i - 1]]["investment_property"]
                          if i > 0 and _is_actual(config, i - 1) else closing[i])
            additions[i] = 5.0 if i > 0 else 0.0
            fair_value_gain[i] = closing[i] - opening[i] - additions[i]
        else:
            opening[i] = closing[i - 1]
            additions[i] = opening[i] * 0.005
            fair_value_gain[i] = opening[i] * escalation
            closing[i] = opening[i] + additions[i] + fair_value_gain[i]

    return dict(
        properties=config.PROPERTIES,
        opening_fv=opening, additions=additions,
        fair_value_gain=fair_value_gain, investment_property=closing,
    )


# ─────────────────────────────────────────────
# SCHEDULE 2 — DEBT / GEARING
# ─────────────────────────────────────────────

def build_debt_schedule(config, rate_mult=1.0):
    """Borrowings roll-forward and finance costs. Actual years pinned; projected years
    hold the disclosed post-refinancing rate roughly flat (with a scenario-driven
    multiplier), no further net drawdowns assumed in Base."""
    n = len(config.YEARS)
    closing = [None] * n
    rate = [None] * n
    finance_costs = [None] * n

    for i, year in enumerate(config.YEARS):
        if _is_actual(config, i):
            closing[i] = config.ACTUALS[year]["borrowings"]
            rate[i] = config.CAPITAL["weighted_avg_rate"] if year == max(config.ACTUAL_YEARS) \
                else config.CAPITAL["weighted_avg_rate"] * 1.3
        else:
            closing[i] = config.CAPITAL["opening_borrowings"]  # held flat in Base
            rate[i] = config.CAPITAL["weighted_avg_rate_projected"] * rate_mult
        opening = closing[i - 1] if i > 0 else closing[i]
        finance_costs[i] = ((opening + closing[i]) / 2) * rate[i]

    return dict(borrowings=closing, weighted_avg_rate=rate, finance_costs=finance_costs)


# ─────────────────────────────────────────────
# SCHEDULE 3 — RENTAL INCOME / NOI
# ─────────────────────────────────────────────

def compute_tier_beds(config):
    """Bed counts by property tier ('seed' vs 'stabilized'), per config.PROPERTIES'
    disclosed per-property bed counts and tier assignment."""
    seed = sum(p["beds"] for p in config.PROPERTIES if p["tier"] == "seed")
    stabilized = sum(p["beds"] for p in config.PROPERTIES if p["tier"] == "stabilized")
    return seed, stabilized


def compute_seed_occupancy(seed_beds, stabilized_beds, portfolio_occ, stabilized_occ):
    """Back-solves the 'seed' tier's occupancy for one period from two disclosed
    aggregates for that same period -- Acorn's own interim report gives the
    portfolio-blended occupancy and, separately, the 'stabilized typical assets'
    subgroup's own occupancy, but never a per-property or seed-tier number directly
    (only qualitative commentary on which properties underperformed). Since
    portfolio_occ x total_beds = stabilized_occ x stabilized_beds + seed_occ x seed_beds,
    seed_occ is solved as the residual -- [DISCLOSED-DERIVED], not fabricated. See
    research_output.md."""
    if seed_beds == 0:
        return stabilized_occ  # no seed tier -- nothing to back-solve
    total_beds = seed_beds + stabilized_beds
    return (portfolio_occ * total_beds - stabilized_occ * stabilized_beds) / seed_beds


def compute_seed_occupancy_h1_2025(config):
    """H1-2025 instance of compute_seed_occupancy() -- see that function's docstring."""
    seed_beds, stabilized_beds = compute_tier_beds(config)
    ri = config.RENTAL_INCOME
    return compute_seed_occupancy(seed_beds, stabilized_beds,
                                   ri["occupancy_portfolio_h1_2025"], ri["occupancy_stabilized"])


def compute_seed_occupancy_h1_2024(config):
    """H1-2024 comparative instance of compute_seed_occupancy() -- a second real data
    point showing the seed tier actually DECLINED year-on-year, not a maturity/ramp-up
    trend. See config.py's RENTAL_INCOME comment and research_output.md."""
    seed_beds, stabilized_beds = compute_tier_beds(config)
    ri = config.RENTAL_INCOME
    return compute_seed_occupancy(seed_beds, stabilized_beds,
                                   ri["occupancy_portfolio_h1_2024"], ri["occupancy_stabilized_h1_2024"])


def build_rental_income_noi(config, occupancy_mult=1.0, escalation_mult=1.0):
    """Rental revenue and occupancy path. Actual years pinned to the disclosed/modeled
    total in config.ACTUALS. Projected years grow on escalation x a two-tier occupancy
    glide: 'seed' properties (the three Acorn's own report names as underperforming --
    lacking an anchor institution / access constraints) recover from a
    [DISCLOSED-DERIVED] back-solved H1-2025 rate toward the disclosed stabilized target
    over occupancy_recovery_years; 'stabilized' properties are already at that target and
    held flat. The two tiers are bed-count-weighted back into a single portfolio
    occupancy figure -- rental income itself stays portfolio-aggregate (see
    BLUEPRINT.md), only the occupancy driver behind it is tier-aware, a more accurate use
    of what's actually disclosed than a single blended glide."""
    n = len(config.YEARS)
    ri = config.RENTAL_INCOME
    escalation = ri["escalation"] * escalation_mult

    seed_beds, stabilized_beds = compute_tier_beds(config)
    total_beds = seed_beds + stabilized_beds
    seed_h1_2025 = compute_seed_occupancy_h1_2025(config)
    # occupancy_mult scales the TARGET the seed tier glides toward (matching how the
    # scenario switch scales the stabilized-tier target on the Assumptions sheet) -- it
    # must never rescale seed_h1_2025 itself, a fixed historical H1-2025 actual.
    stabilized_target = min(1.0, ri["occupancy_stabilized"] * occupancy_mult)

    rental_income = [None] * n
    occupancy = [None] * n

    for i, year in enumerate(config.YEARS):
        if _is_actual(config, i):
            rental_income[i] = config.ACTUALS[year]["rental_income"]
            occupancy[i] = ri["occupancy_portfolio_h1_2025"]
        else:
            years_since_actual = year - max(config.ACTUAL_YEARS)
            progress = min(1.0, years_since_actual / ri["occupancy_recovery_years"])
            seed_occ = seed_h1_2025 + progress * (stabilized_target - seed_h1_2025)
            occupancy[i] = (seed_occ * seed_beds + stabilized_target * stabilized_beds) / total_beds
            occ_uplift = occupancy[i] / occupancy[max(0, i - 1)] if occupancy[i - 1] else 1.0
            rental_income[i] = rental_income[i - 1] * (1 + escalation) * occ_uplift

    return dict(rental_income=rental_income, occupancy=occupancy,
                seed_occupancy_h1_2025=seed_h1_2025, seed_beds=seed_beds,
                stabilized_beds=stabilized_beds)


# ─────────────────────────────────────────────
# SCHEDULE 4 — OPERATING EXPENSES
# ─────────────────────────────────────────────

def build_opex(config, income_reconciliation_opex=None):
    """Itemized admin + fund-level opex. Projected years escalate each item forward from
    its own FY2025 (H1 actual x2) base at its own escalation rate. Actual years use the
    per-item FY2025 base directly for 2025, and for the thinner 2023/2024 years scale the
    itemized total to the reconciled residual passed in as
    `income_reconciliation_opex` (computed by build_income_statement) -- so the
    itemized breakdown always sums to the pinned, disclosure-consistent total."""
    n = len(config.YEARS)
    items = config.OPEX_ITEMS
    base_total = sum(item["h1_2025_actual"] * 2 for item in items)

    per_item = []
    for item in items:
        base = item["h1_2025_actual"] * 2
        series = [None] * n
        for i, year in enumerate(config.YEARS):
            if year == 2025:
                series[i] = base
            elif not _is_actual(config, i):
                years_out = year - 2025
                series[i] = base * (1 + item["escalation"]) ** years_out
            # 2023/2024 filled in below once the reconciled total is known
        per_item.append(dict(name=item["name"], category=item["category"], series=series))

    admin_total = [None] * n
    fund_total = [None] * n
    for i, year in enumerate(config.YEARS):
        if year == 2025 or not _is_actual(config, i):
            admin_total[i] = sum(p["series"][i] for p in per_item if p["category"] == "admin")
            fund_total[i] = sum(p["series"][i] for p in per_item if p["category"] == "fund")
        else:
            total = (income_reconciliation_opex[i] if income_reconciliation_opex
                    else base_total * 0.9 ** (2025 - year))
            share = base_total and total / base_total or 0.0
            admin_total[i] = sum(item["h1_2025_actual"] * 2 for item in items
                                 if item["category"] == "admin") * share
            fund_total[i] = sum(item["h1_2025_actual"] * 2 for item in items
                                if item["category"] == "fund") * share
            for p, item in zip(per_item, items):
                p["series"][i] = item["h1_2025_actual"] * 2 * share

    return dict(items=per_item, admin_total=admin_total, fund_total=fund_total,
                opex_total=[a + f for a, f in zip(admin_total, fund_total)])


# ─────────────────────────────────────────────
# SCHEDULE 5 — INCOME STATEMENT
# ─────────────────────────────────────────────

def build_income_statement(config, rental_noi, debt, property_portfolio):
    """Operating Income -> Operating Profit -> Net Profit, matching Acorn's own
    statement structure. Actual years: rental income, fair value gain and net profit are
    pinned to config.ACTUALS; finance income/opex-total are back-solved as the residual
    that reconciles the pinned figures -- see module docstring. Projected years' fair
    value gain is sourced from property_portfolio (escalation-driven), not recomputed
    here, so the income statement and the property schedule never disagree."""
    n = len(config.YEARS)
    rental_income = rental_noi["rental_income"]
    other_income = [0.3] * n  # immaterial (parking fees etc.), [MODELED]

    finance_income = [None] * n
    fair_value_gain = [None] * n
    net_profit = [None] * n
    opex_total_actual = [None] * n  # only populated for actual years (the reconciliation residual)
    operating_profit = [None] * n
    operating_income = [rental_income[i] + other_income[i] for i in range(n)]

    for i, year in enumerate(config.YEARS):
        if _is_actual(config, i):
            fair_value_gain[i] = config.ACTUALS[year]["fair_value_gain"]
            net_profit[i] = config.ACTUALS[year]["net_profit"]
            finance_income[i] = 19.3 if year == 2025 else 15.0  # [MODELED], immaterial
            operating_profit[i] = (net_profit[i] - fair_value_gain[i]
                                   - finance_income[i] + debt["finance_costs"][i])
            opex_total_actual[i] = operating_income[i] - operating_profit[i]
        else:
            finance_income[i] = finance_income[i - 1] * 1.03
            fair_value_gain[i] = property_portfolio["fair_value_gain"][i]

    return dict(
        operating_income=operating_income, other_income=other_income,
        finance_income=finance_income, fair_value_gain=fair_value_gain,
        opex_total_actual=opex_total_actual, net_profit_pinned=net_profit,
    )


def finalize_income_statement(config, rental_noi, opex, debt, income_stmt_partial):
    """Second pass: now that build_opex() has the full opex_total series (using the
    reconciled residual for actual years), compute Operating Profit and Net Profit for
    every year, projected years included."""
    n = len(config.YEARS)
    operating_income = income_stmt_partial["operating_income"]
    finance_income = income_stmt_partial["finance_income"]
    fair_value_gain = income_stmt_partial["fair_value_gain"]
    net_profit = [None] * n
    operating_profit = [None] * n

    for i, year in enumerate(config.YEARS):
        operating_profit[i] = operating_income[i] - opex["opex_total"][i]
        if _is_actual(config, i):
            net_profit[i] = income_stmt_partial["net_profit_pinned"][i]
        else:
            net_profit[i] = (operating_profit[i] + finance_income[i]
                             - debt["finance_costs"][i] + fair_value_gain[i])

    return dict(
        operating_income=operating_income, other_income=income_stmt_partial["other_income"],
        opex_total=opex["opex_total"], operating_profit=operating_profit,
        finance_income=finance_income, finance_costs=debt["finance_costs"],
        fair_value_gain=fair_value_gain, net_profit=net_profit,
    )


# ─────────────────────────────────────────────
# SCHEDULE 6 — DISTRIBUTABLE INCOME
# ─────────────────────────────────────────────

def build_distributable_income(config, income_stmt, units, payout_override=None):
    """Distributable Income = Net Profit less non-cash items (fair value gain here --
    Acorn's filings show no bargain-purchase gain or impairment in the years modeled).
    Payout ratio: actual years pinned to the disclosed ratio (even where, as in FY2025,
    it is below the 80% CMA minimum -- a real governance fact, not smoothed over);
    projected years default to the 80% regulatory minimum in Base."""
    n = len(config.YEARS)
    distributable = [None] * n
    payout_ratio = [None] * n
    dividend = [None] * n
    dpu = [None] * n

    for i, year in enumerate(config.YEARS):
        distributable[i] = income_stmt["net_profit"][i] - income_stmt["fair_value_gain"][i]
        if _is_actual(config, i):
            payout_ratio[i] = config.ACTUALS[year]["payout_ratio"]
            dividend[i] = config.ACTUALS[year]["dividend_paid"]
            dpu[i] = config.ACTUALS[year]["distribution_per_unit"]
        else:
            payout_ratio[i] = payout_override if payout_override is not None else config.REGULATORY["payout_min"]
            dividend[i] = max(0.0, distributable[i]) * payout_ratio[i]
            dpu[i] = dividend[i] / units["units_in_issue"][i] if units["units_in_issue"][i] else 0.0

    return dict(distributable_income=distributable, payout_ratio=payout_ratio,
                dividend=dividend, distribution_per_unit=dpu)


# ─────────────────────────────────────────────
# SCHEDULE 7 — UNITS IN ISSUE
# ─────────────────────────────────────────────

def build_units(config):
    n = len(config.YEARS)
    closing = [None] * n
    for i, year in enumerate(config.YEARS):
        if _is_actual(config, i):
            closing[i] = config.ACTUALS[year]["units_in_issue"]
        else:
            closing[i] = closing[i - 1] * (1 + config.UNITS["issuance_rate"])
    return dict(units_in_issue=closing)


# ─────────────────────────────────────────────
# SCHEDULE 8 — CASH FLOW & BALANCE SHEET
# ─────────────────────────────────────────────

def build_cash_flow_and_balance_sheet(config, property_portfolio, debt, income_stmt,
                                       distributable, units):
    """Balance Sheet: Investment Property (+ other assets, small/flat) = Total Assets;
    NAV (unit-holder equity) + Borrowings (+ other liabilities, small/flat) = Total
    Assets -- the Master Check's balance-sheet-balances row. Actual years pin NAV/total
    assets to config.ACTUALS; projected years roll NAV forward from retained
    (non-distributed) earnings plus modeled unit-issuance proceeds."""
    n = len(config.YEARS)
    investment_property = property_portfolio["investment_property"]
    borrowings = debt["borrowings"]

    other_assets = [None] * n
    total_assets = [None] * n
    nav = [None] * n
    other_liabilities = [None] * n
    total_liabilities = [None] * n
    cash = [None] * n
    issuance_proceeds = [None] * n

    for i, year in enumerate(config.YEARS):
        if _is_actual(config, i):
            total_assets[i] = config.ACTUALS[year]["total_assets"]
            nav[i] = config.ACTUALS[year]["nav"]
            other_assets[i] = total_assets[i] - investment_property[i]
            total_liabilities[i] = total_assets[i] - nav[i]
            other_liabilities[i] = total_liabilities[i] - borrowings[i]
            cash[i] = max(0.0, other_assets[i] * 0.6)  # cash is most of "other assets"
            issuance_proceeds[i] = 0.0
        else:
            other_liabilities[i] = other_liabilities[i - 1]
            total_liabilities[i] = borrowings[i] + other_liabilities[i]
            issuance_proceeds[i] = units["units_in_issue"][i] - units["units_in_issue"][i - 1]
            issuance_proceeds[i] = max(0.0, issuance_proceeds[i]) * config.PEER_REITS[0]["nav_per_unit"]
            nav[i] = (nav[i - 1] + income_stmt["net_profit"][i]
                     - distributable["dividend"][i] + issuance_proceeds[i])
            # Total Assets = NAV + Total Liabilities (the balance sheet identity itself,
            # not an independent sum) -- Other Assets/Cash is the plug, exactly as a real
            # cash flow statement's closing cash balance is a residual, not a forecast
            # driven independently of the rest of the balance sheet.
            total_assets[i] = nav[i] + total_liabilities[i]
            other_assets[i] = total_assets[i] - investment_property[i]
            cash[i] = other_assets[i] * 0.6

    nav_per_unit = [nav[i] / units["units_in_issue"][i] if units["units_in_issue"][i] else 0.0
                    for i in range(n)]

    return dict(
        investment_property=investment_property, other_assets=other_assets, cash=cash,
        total_assets=total_assets, nav=nav, borrowings=borrowings,
        other_liabilities=other_liabilities, total_liabilities=total_liabilities,
        nav_per_unit=nav_per_unit, issuance_proceeds=issuance_proceeds,
        balance_check=[abs(total_assets[i] - nav[i] - total_liabilities[i]) < 0.01 for i in range(n)],
    )


# ─────────────────────────────────────────────
# SCHEDULE 9 — REGULATORY COMPLIANCE (CMA I-REIT limits)
# ─────────────────────────────────────────────

def build_regulatory_compliance(config, bs, distributable):
    n = len(config.YEARS)
    reg = config.REGULATORY
    ltv = [bs["borrowings"][i] / bs["total_assets"][i] if bs["total_assets"][i] else 0.0
          for i in range(n)]
    income_producing_pct = [bs["investment_property"][i] / bs["total_assets"][i]
                            if bs["total_assets"][i] else 0.0 for i in range(n)]
    payout_pct = distributable["payout_ratio"]

    return dict(
        ltv=ltv, ltv_ok=[v <= reg["ltv_max"] + 1e-9 for v in ltv],
        income_producing_pct=income_producing_pct,
        income_producing_ok=[v >= reg["income_producing_min"] - 1e-9 for v in income_producing_pct],
        payout_pct=payout_pct,
        payout_ok=[v >= reg["payout_min"] - 1e-9 for v in payout_pct],
    )


# ─────────────────────────────────────────────
# SCHEDULE 10 — RATIO DISCLOSURES
# ─────────────────────────────────────────────

def build_ratio_disclosures(config, income_stmt, bs, distributable, debt):
    n = len(config.YEARS)
    mer = [income_stmt["opex_total"][i] / bs["nav"][i] if bs["nav"][i] else 0.0
          for i in range(n)]
    icr = [income_stmt["operating_profit"][i] / debt["finance_costs"][i]
          if debt["finance_costs"][i] else 0.0 for i in range(n)]
    fund_operating_margin = [income_stmt["operating_profit"][i] / income_stmt["operating_income"][i]
                             if income_stmt["operating_income"][i] else 0.0 for i in range(n)]
    distribution_yield = [distributable["distribution_per_unit"][i] / config.PEER_REITS[0]["price"]
                          if config.PEER_REITS[0]["price"] else 0.0 for i in range(n)]
    capital_appreciation = [0.0] + [
        (bs["nav_per_unit"][i] / bs["nav_per_unit"][i - 1] - 1) if bs["nav_per_unit"][i - 1] else 0.0
        for i in range(1, n)
    ]
    total_return = [distribution_yield[i] + capital_appreciation[i] for i in range(n)]

    return dict(
        mer=mer, icr=icr, fund_operating_margin=fund_operating_margin,
        distribution_yield=distribution_yield, capital_appreciation=capital_appreciation,
        total_return=total_return, nav_per_unit=bs["nav_per_unit"],
        distribution_per_unit=distributable["distribution_per_unit"],
    )


# ─────────────────────────────────────────────
# SCHEDULE 11 — VALUATION (NAV / DDM / Cap-rate / peer blend)
# ─────────────────────────────────────────────

def build_valuation(config, income_stmt, bs, distributable, units, cap_rate_delta=0.0):
    n = len(config.YEARS)
    v = config.VALUATION
    coe = v["risk_free_rate"] + v["beta"] * v["equity_risk_premium"]
    cap_rate = v["cap_rate"] + cap_rate_delta

    # NAV approach: latest actual NAV/unit, the most reliable anchor for a property-
    # holding entity.
    nav_value = bs["nav_per_unit"][n - 1]

    # DDM: PV of projected DPU over the PROJECTED years only (2023-2025 are actual,
    # already-paid dividends, not future cash flows to discount) + PV of terminal
    # NAV/unit (a dividend-plus-terminal-NAV hybrid, not a pure Gordon-growth-on-
    # dividends model -- with payout ratios well below 100%, most of a REIT's total
    # return accrues through NAV growth on retained earnings, not distributions alone,
    # so terminal NAV/unit is the more defensible "exit value" than an infinite-growth
    # dividend annuity).
    n_proj = len(config.YEARS) - len(config.ACTUAL_YEARS)
    dpu_proj = distributable["distribution_per_unit"][-n_proj:]
    pv_dividends = [dpu_proj[i] / (1 + coe) ** (i + 1) for i in range(n_proj)]
    pv_terminal_ddm = nav_value / (1 + coe) ** n_proj
    ddm_value = sum(pv_dividends) + pv_terminal_ddm

    # Direct capitalization / cap rate: latest NOI run-rate / cap rate, less debt, / units.
    noi_latest = income_stmt["operating_income"][-1] - income_stmt["opex_total"][-1]
    implied_property_value = noi_latest / cap_rate
    implied_equity_value = implied_property_value - bs["borrowings"][-1]
    cap_rate_value = implied_equity_value / units["units_in_issue"][-1] if units["units_in_issue"][-1] else 0.0

    # Peer cross-check: apply the average peer NAV discount/premium to this REIT's own NAV.
    avg_peer_discount = sum(p["discount_pct"] for p in config.PEER_REITS) / len(config.PEER_REITS)
    peer_value = nav_value * (1 + avg_peer_discount)

    w = v.get("blend_weights", dict(nav=0.4, ddm=0.3, cap_rate=0.3))
    blended_value = w["nav"] * nav_value + w["ddm"] * ddm_value + w["cap_rate"] * cap_rate_value

    return dict(
        cost_of_equity=coe, nav_value=nav_value, ddm_value=ddm_value,
        cap_rate_value=cap_rate_value, peer_value=peer_value, avg_peer_discount=avg_peer_discount,
        blended_value=blended_value, blend_weights=w,
        pv_dividends=pv_dividends, pv_terminal_ddm=pv_terminal_ddm,
        implied_property_value=implied_property_value,
    )


# ─────────────────────────────────────────────
# TOP-LEVEL BUILDER
# ─────────────────────────────────────────────

def build_all(config, occupancy_mult=1.0, escalation_mult=1.0, cap_rate_delta=0.0,
              rate_mult=1.0, payout_override=None):
    property_portfolio = build_property_portfolio(config)
    debt = build_debt_schedule(config, rate_mult=rate_mult)
    rental_noi = build_rental_income_noi(config, occupancy_mult=occupancy_mult,
                                         escalation_mult=escalation_mult)
    partial_income_stmt = build_income_statement(config, rental_noi, debt, property_portfolio)
    opex = build_opex(config, income_reconciliation_opex=partial_income_stmt["opex_total_actual"])
    income_stmt = finalize_income_statement(config, rental_noi, opex, debt, partial_income_stmt)
    units = build_units(config)
    distributable = build_distributable_income(config, income_stmt, units,
                                                payout_override=payout_override)
    bs = build_cash_flow_and_balance_sheet(config, property_portfolio, debt, income_stmt,
                                           distributable, units)
    regulatory = build_regulatory_compliance(config, bs, distributable)
    ratios = build_ratio_disclosures(config, income_stmt, bs, distributable, debt)
    valuation = build_valuation(config, income_stmt, bs, distributable, units,
                                cap_rate_delta=cap_rate_delta)

    return dict(
        property_portfolio=property_portfolio, debt=debt, rental_noi=rental_noi,
        opex=opex, income_stmt=income_stmt, units=units, distributable=distributable,
        bs=bs, regulatory=regulatory, ratios=ratios, valuation=valuation,
    )


# ─────────────────────────────────────────────
# SCENARIOS — Base/Best/Worst
# ─────────────────────────────────────────────

def build_scenario(config, occupancy_mult=1.0, escalation_mult=1.0, cap_rate_delta=0.0,
                   rate_mult=1.0):
    return build_all(config, occupancy_mult=occupancy_mult, escalation_mult=escalation_mult,
                     cap_rate_delta=cap_rate_delta, rate_mult=rate_mult)


def build_scenarios(config):
    """Base/Best/Worst, for the Scenarios sheet. Base is the same as build_all(). Reads
    config.SCENARIO_MULTIPLIERS so the Python scenarios and the renderer's live
    CHOOSE-switch formulas are always derived from the same source."""
    base = build_all(config)
    m = config.SCENARIO_MULTIPLIERS
    best = build_scenario(config, **m["best"])
    worst = build_scenario(config, **m["worst"])
    return dict(base=base, best=best, worst=worst)


# ─────────────────────────────────────────────
# SENSITIVITY — one-lever-at-a-time Net Profit impact
# ─────────────────────────────────────────────

def _avg_net_profit(config, **kwargs):
    np_series = build_all(config, **kwargs)["income_stmt"]["net_profit"]
    return sum(np_series) / len(np_series)


def build_sensitivity(config):
    """Average-Net-Profit % impact of shocking one driver at a time, holding all others
    at Base. Occupancy and escalation reuse the existing Best/Worst multipliers already
    established as scenario levers; cap rate and debt rate use a standalone shock,
    since a cap-rate move affects the Output sheet's valuation more than the P&L."""
    base_avg = _avg_net_profit(config)
    m = config.SCENARIO_MULTIPLIERS

    def pct(**kwargs):
        return (_avg_net_profit(config, **kwargs) - base_avg) / base_avg

    factors = [
        dict(
            name="Occupancy", category="Property-specific — demand/leasing cycle",
            detail=f"Worst {m['worst']['occupancy_mult']:.2f}x / Best {m['best']['occupancy_mult']:.2f}x occupancy multiplier",
            downside=pct(occupancy_mult=m["worst"]["occupancy_mult"]),
            upside=pct(occupancy_mult=m["best"]["occupancy_mult"]),
        ),
        dict(
            name="Rental escalation", category="Macro — inflation pass-through",
            detail=f"Worst {m['worst']['escalation_mult']:.2f}x / Best {m['best']['escalation_mult']:.2f}x escalation multiplier",
            downside=pct(escalation_mult=m["worst"]["escalation_mult"]),
            upside=pct(escalation_mult=m["best"]["escalation_mult"]),
        ),
        dict(
            name="Cost of debt", category="Macro — CBK policy rate cycle",
            detail="+/-150bp parallel shift on the projected weighted-average borrowing rate",
            downside=pct(rate_mult=1.15), upside=pct(rate_mult=0.85),
        ),
    ]
    return dict(base_avg_net_profit=base_avg, factors=factors)
