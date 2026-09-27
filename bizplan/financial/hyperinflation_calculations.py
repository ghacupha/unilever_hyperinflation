"""Ground-truth Python engine for the Unilever hyperinflation-accounting model
(CFA LII Multinational Operations, IAS 29 / IAS 21).

For each hyperinflationary subsidiary (Argentina, Türkiye) and year, computes three
parallel "worlds" from the same local-currency nominal inputs:

  World A — plain current-rate method: no inflation restatement; balance sheet at the
            closing FX rate, income statement at the average FX rate. This is the
            "disappearing plant" baseline the IAS 29 impact is measured against.
  World B — US GAAP temporal method: monetary items at the current (closing) rate,
            non-monetary items at historical rates, most P&L at the average rate. The
            resulting plug is an FX *remeasurement* gain/loss, not a purchasing-power
            monetary gain/loss — a different mechanism from World C, not just a
            different number.
  World C — actual IFRS treatment (IAS 29 restatement, then IAS 21 translation of the
            restated figures at the closing rate) — this is what Unilever actually
            reports.

The IAS 29 net monetary gain/(loss) and the World B remeasurement gain/(loss) are each
computed as a balancing plug (restated/remeasured Assets − Liabilities − Equity − Net
income), which is how IAS 29 works in practice and guarantees the restated balance
sheet ties out by construction rather than by an approximate formula.

Non-monetary opening balances are assumed already stated in prior-year-end purchasing
power (i.e., they are last year's IAS 29-restated closing figures) and are restated by
a single index_close/index_open factor; in-year flows (revenue, costs, capex) are
assumed to accrue evenly through the year and restated by index_close/index_avg, where
index_avg is the geometric mean of the opening and closing index — this is what keeps
the whole engine hand-traceable rather than requiring a monthly index/FX series.
"""


def _geo_mean(a, b):
    return (a * b) ** 0.5


def restate_and_translate(local, idx_open, idx_close, fx_open, fx_close, idx_avg=None, fx_avg=None):
    """local: dict of nominal local-currency figures for the year —
    rev, cogs, opex, dep, capex, nonmon_assets_open, mon_assets_close, mon_liab_close,
    equity_open (opening equity, already prior-year-restated), and optional nonmon_liab.
    Returns {'A':..., 'B':..., 'C':...}, each a dict of EUR figures."""
    idx_avg = idx_avg or _geo_mean(idx_open, idx_close)
    fx_avg = fx_avg or _geo_mean(fx_open, fx_close)
    f_close = idx_close / idx_open
    f_avg = idx_close / idx_avg
    nonmon_liab = local.get("nonmon_liab", 0.0)

    # ---- World C: IAS 29 restatement (local, year-end purchasing power), then IAS 21
    # translation of the restated figures at the closing rate ----
    r_rev, r_cogs, r_opex, r_dep = (local[k] * f_avg for k in ("rev", "cogs", "opex", "dep"))
    r_op_profit = r_rev - r_cogs - r_opex - r_dep
    r_nonmon_assets = local["nonmon_assets_open"] * f_close + local["capex"] * f_avg - r_dep
    r_total_assets = r_nonmon_assets + local["mon_assets_close"]
    r_total_liab = local["mon_liab_close"] + nonmon_liab
    r_equity_open = local["equity_open"] * f_close
    monetary_gain_loss = (r_total_assets - r_total_liab) - r_equity_open - r_op_profit

    C = dict(
        revenue=r_rev / fx_close, cogs=r_cogs / fx_close, opex=r_opex / fx_close,
        depreciation=r_dep / fx_close, operating_profit=r_op_profit / fx_close,
        total_assets=r_total_assets / fx_close, non_monetary_assets=r_nonmon_assets / fx_close,
        equity=(r_total_assets - r_total_liab) / fx_close, monetary_gain_loss=monetary_gain_loss / fx_close,
    )

    # ---- World A: plain current-rate method (no restatement) ----
    n_nonmon_assets = local["nonmon_assets_open"] + local["capex"] - local["dep"]
    n_total_assets = n_nonmon_assets + local["mon_assets_close"]
    n_total_liab = local["mon_liab_close"] + nonmon_liab
    A = dict(
        revenue=local["rev"] / fx_avg, cogs=local["cogs"] / fx_avg, opex=local["opex"] / fx_avg,
        depreciation=local["dep"] / fx_avg,
        operating_profit=(local["rev"] - local["cogs"] - local["opex"] - local["dep"]) / fx_avg,
        total_assets=n_total_assets / fx_close, non_monetary_assets=n_nonmon_assets / fx_close,
        equity=(n_total_assets - n_total_liab) / fx_close, monetary_gain_loss=0.0,
    )

    # ---- World B: US GAAP temporal method (remeasurement) ----
    b_nonmon_assets = (local["nonmon_assets_open"] / fx_open + local["capex"] / fx_avg
                       - local["dep"] / fx_avg)
    b_mon_assets = local["mon_assets_close"] / fx_close
    b_mon_liab = local["mon_liab_close"] / fx_close + nonmon_liab / fx_close
    b_equity_open = local["equity_open"] / fx_open
    b_op_profit = (local["rev"] - local["cogs"] - local["opex"] - local["dep"]) / fx_avg
    remeasurement_gain_loss = (b_nonmon_assets + b_mon_assets) - b_mon_liab - b_equity_open - b_op_profit
    B = dict(
        revenue=local["rev"] / fx_avg, cogs=local["cogs"] / fx_avg, opex=local["opex"] / fx_avg,
        depreciation=local["dep"] / fx_avg, operating_profit=b_op_profit,
        total_assets=b_nonmon_assets + b_mon_assets, non_monetary_assets=b_nonmon_assets,
        equity=(b_nonmon_assets + b_mon_assets) - b_mon_liab, monetary_gain_loss=remeasurement_gain_loss,
    )

    return dict(A=A, B=B, C=C)


def impact_vs_current_rate(worlds):
    """The 'IAS 29 impact' table Unilever discloses: World C minus World A."""
    A, C = worlds["A"], worlds["C"]
    return dict(
        total_assets=C["total_assets"] - A["total_assets"],
        turnover=C["revenue"] - A["revenue"],
        operating_profit=C["operating_profit"] - A["operating_profit"],
        net_monetary_gain_loss=C["monetary_gain_loss"],
    )


def restated_closing_local(local, idx_open, idx_close, fx_open, fx_close):
    """Non-monetary assets and equity restated to closing local purchasing power, in
    LOCAL currency (not translated) — the basis a following year's 'opening, already
    prior-year-restated' inputs roll forward from."""
    idx_avg = _geo_mean(idx_open, idx_close)
    f_close, f_avg = idx_close / idx_open, idx_close / idx_avg
    r_dep = local["dep"] * f_avg
    r_nonmon_assets = local["nonmon_assets_open"] * f_close + local["capex"] * f_avg - r_dep
    r_op_profit = (local["rev"] * f_avg - local["cogs"] * f_avg - local["opex"] * f_avg - r_dep)
    r_equity_open = local["equity_open"] * f_close
    r_total_assets = r_nonmon_assets + local["mon_assets_close"]
    r_total_liab = local["mon_liab_close"] + local.get("nonmon_liab", 0.0)
    monetary_gain_loss = (r_total_assets - r_total_liab) - r_equity_open - r_op_profit
    closing_equity = r_equity_open + r_op_profit + monetary_gain_loss
    return dict(nonmon_assets_close=r_nonmon_assets, equity_close=closing_equity)


def consolidate(subsidiary_worlds, other_ops_eur):
    """subsidiary_worlds: {name: {'A':..,'B':..,'C':..}}. other_ops_eur: dict of the
    rest of the group's EUR figures (same line-item shape), assumed scenario-invariant
    (they're not hyperinflationary, so World A/B/C only differ by subsidiary)."""
    out = {}
    for world in ("A", "B", "C"):
        total = dict(other_ops_eur)
        for sub in subsidiary_worlds.values():
            for k, v in sub[world].items():
                total[k] = total.get(k, 0.0) + v
        out[world] = total
    return out


def ratios(world):
    revenue, total_assets, equity = world["revenue"], world["total_assets"], world["equity"]
    total_liab = total_assets - equity
    return dict(
        roa=world["operating_profit"] / total_assets if total_assets else 0.0,
        asset_turnover=revenue / total_assets if total_assets else 0.0,
        debt_to_equity=total_liab / equity if equity else 0.0,
    )


def scenario_comparison_table(consolidated_worlds):
    """Revenue/COGS/OpProfit/PPE/TotalAssets/Equity/monetary-gain-loss/ROA/AssetTurnover/D-E
    for World A/B/C side by side — the table shape the user asked for."""
    rows = ["revenue", "cogs", "operating_profit", "non_monetary_assets", "total_assets",
            "equity", "monetary_gain_loss"]
    table = {row: {w: consolidated_worlds[w][row] for w in ("A", "B", "C")} for row in rows}
    for w in ("A", "B", "C"):
        r = ratios(consolidated_worlds[w])
        for k, v in r.items():
            table.setdefault(k, {})[w] = v
    return table


def validate_against_disclosed(model_impact, disclosed_impact):
    """model_impact / disclosed_impact: dicts with total_assets/turnover/operating_profit/
    net_monetary_gain_loss keys (EURm). Returns per-line absolute and % gaps."""
    gap = {}
    for k in ("total_assets", "turnover", "operating_profit", "net_monetary_gain_loss"):
        m, d = model_impact.get(k, 0.0), disclosed_impact.get(k, 0.0)
        gap[k] = dict(model=m, disclosed=d, abs_gap=m - d,
                      pct_gap=(m - d) / d if d else None, same_sign=(m >= 0) == (d >= 0))
    return gap


def build_model(config):
    """Single entry point: runs every subsidiary through World A/B/C for every year in
    config.YEARS, consolidates with the rest of the group, and validates 2024's impact
    against config.DISCLOSED_IMPACT_2024 / later years against config.VALIDATION_ACTUALS.
    Returns {year: {'subsidiaries': {name: {'worlds':.., 'impact':..}}, 'consolidated':..,
    'comparison':.., 'validation': {name: gap_dict} or None}}."""
    result = {}
    for year in config.YEARS:
        sub_worlds, sub_impact = {}, {}
        for name in config.SUBSIDIARIES:
            local = config.ACTUALS[name][year]
            idx = config.INFLATION_INDICES[name][year]
            fx = config.FX_RATES[name][year]
            worlds = restate_and_translate(local, idx["index_open"], idx["index_close"],
                                            fx["fx_open"], fx["fx_close"])
            sub_worlds[name] = worlds
            sub_impact[name] = impact_vs_current_rate(worlds)

        consolidated = consolidate(sub_worlds, config.OTHER_GROUP_OPERATIONS_EUR)
        comparison = scenario_comparison_table(consolidated)

        disclosed = (config.DISCLOSED_IMPACT_2024 if year == min(config.YEARS)
                     else config.VALIDATION_ACTUALS)
        validation = None
        if disclosed:
            validation = {name: validate_against_disclosed(sub_impact[name], disclosed[name])
                          for name in config.SUBSIDIARIES if name in disclosed}

        result[year] = dict(subsidiaries={n: dict(worlds=sub_worlds[n], impact=sub_impact[n])
                                          for n in config.SUBSIDIARIES},
                             consolidated=consolidated, comparison=comparison,
                             validation=validation)
    return result
