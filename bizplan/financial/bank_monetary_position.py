# Copyright (c) 2026 Edwin Njeru. Licensed under the MIT License (see LICENSE).

"""Bank net-monetary-position reconstruction — Garanti BBVA "advanced case" (BLUEPRINT.md
Phase 5, formerly BACKLOG.md's deferred Phase 5).

Structurally different exercise from `hyperinflation_calculations.py`'s Unilever model:
there, a fictional subsidiary is algebraically *solved* so its net monetary gain/(loss)
plug matches Unilever's real disclosed aggregate impact by construction. Here, every
input is Garanti BBVA's own real disclosed balance sheet, and the net monetary result is
*independently estimated* from a classification + CPI series, then checked against
Garanti's own disclosed "Gain/(loss) on net monetary position, net" line — an actual
attempt at reconstruction, not a calibration, and the resulting gap is reported rather
than tuned away.

Mechanics (see `examples/garanti_bbva/research_output.md` for the full worked derivation):

1. Classify each balance-sheet line as monetary or non-monetary (`config.BALANCE_SHEET`
   carries this per line, since a bank's classification is mostly mechanical — cash,
   loans, deposits, debt are monetary; PP&E, investment property, equity investments,
   deferred tax are not).
2. Garanti's own FY2025 report presents its FY2024 comparative column already restated
   into FY2025 purchasing-power terms (IAS 29 ¶34 requires comparatives to be re-expressed
   in the current period's measuring unit). To estimate FY2025's monetary result we need
   the opening (1 Jan 2025 = 31 Dec 2024) net monetary position in *its own* (FY2024)
   purchasing-power terms, so step one is to divide the as-shown comparative back out by
   the CPI ratio.
3. Estimate the monetary gain/(loss) for the year as the opening net monetary position
   (recovered to its own period's purchasing power) times the period's inflation rate,
   sign-flipped (a net monetary *asset* position loses purchasing power as prices rise; a
   net monetary *liability* position gains) — the standard single-period approximation,
   same "known simplification" category as `hyperinflation_calculations.py`'s
   geometric-mean-average-index substitute for a full monthly series.
4. Compare the estimate to Garanti's actual disclosed figure and report the gap — not
   resolved, since resolving it would mean tuning the classification/approximation until
   it matches, which defeats the point of using real, independently-sourced data.
"""


def monetary_totals(balance_sheet, year, side):
    """Sum of lines flagged monetary=True (or False) on one side ('assets' or
    'liabilities') for a given year, as published (i.e. both years in the same
    reporting-date purchasing-power terms, per the source statement's own convention)."""
    year_key = str(year)
    return {
        "monetary": sum(v[year_key] for v in balance_sheet[side].values() if v["monetary"]),
        "non_monetary": sum(v[year_key] for v in balance_sheet[side].values() if not v["monetary"]),
    }


def net_monetary_position(balance_sheet, year):
    """Net monetary position (monetary assets - monetary liabilities) as published, i.e.
    in the purchasing-power terms of the report's own latest year-end (both FY2024 and
    FY2025 columns in a FY2025 report are expressed in Dec-2025 terms)."""
    assets = monetary_totals(balance_sheet, year, "assets")["monetary"]
    liabilities = monetary_totals(balance_sheet, year, "liabilities")["monetary"]
    return assets - liabilities


def recover_original_purchasing_power(value_as_shown, shown_in_year, original_year, cpi_index):
    """Undo IAS 29 ¶34's comparative-restatement: `value_as_shown` is expressed in
    `shown_in_year`'s year-end purchasing power; recover what it would have been in
    `original_year`'s own year-end purchasing power."""
    return value_as_shown * cpi_index[original_year] / cpi_index[shown_in_year]


def estimate_monetary_result(config, year):
    """Single-period approximation of the monetary gain/(loss) for `year`: opening net
    monetary position (recovered to its own period-end purchasing power) times the
    period's CPI growth rate, sign-flipped. Returns None if the prior year's own balance
    isn't available (no FY(year-2) column to recover from)."""
    prior_year = year - 1
    if (prior_year - 1) not in config.CPI_INDEX:
        return None  # can't recover prior_year's own purchasing power without its own opening index

    nmp_prior_as_shown = net_monetary_position(config.BALANCE_SHEET, prior_year)
    nmp_prior_original = recover_original_purchasing_power(
        nmp_prior_as_shown, shown_in_year=year, original_year=prior_year,
        cpi_index=config.CPI_INDEX,
    )
    growth = config.CPI_INDEX[year] / config.CPI_INDEX[prior_year] - 1
    return -nmp_prior_original * growth


def compare_to_disclosed(config, year):
    """Estimate vs. Garanti's own disclosed net-monetary-result line for `year`. Returns
    None if no estimate is possible (see `estimate_monetary_result`)."""
    estimate = estimate_monetary_result(config, year)
    if estimate is None:
        return None
    disclosed = config.DISCLOSED_NET_MONETARY_RESULT[str(year)]
    return {
        "estimate": estimate,
        "disclosed": disclosed,
        "gap": estimate - disclosed,
        "gap_multiple": estimate / disclosed if disclosed else None,
    }


def build_model(config):
    """Single entry point: classification totals, net monetary position, and the
    estimate-vs-disclosed comparison for every year with the data to support it."""
    result = {"years": {}}
    for year in config.YEARS:
        result["years"][year] = {
            "assets": monetary_totals(config.BALANCE_SHEET, year, "assets"),
            "liabilities": monetary_totals(config.BALANCE_SHEET, year, "liabilities"),
            "net_monetary_position": net_monetary_position(config.BALANCE_SHEET, year),
            "disclosed_net_monetary_result": config.DISCLOSED_NET_MONETARY_RESULT[str(year)],
            "comparison": compare_to_disclosed(config, year),
        }
    return result
