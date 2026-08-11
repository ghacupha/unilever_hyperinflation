"""Pure-Python re-implementation of the Model sheet's "Master Check" section
(reit_excel_renderer.py::_build_master_check) — lets a pipeline gate on model integrity
without a spreadsheet engine. Mirrors the same four checks and tolerances so a workbook
and this validator never disagree about what "OK" means:

- Balance Sheet Check: Total Assets = NAV + Total Liabilities, within 0.01
- LTV Check: Borrowings / Total Assets <= CMA gearing limit (35%)
- Income-Producing Check: Investment Property / Total Assets >= CMA minimum (75%)
- Payout Check: Distribution payout ratio >= CMA minimum (80%)

The Payout Check is expected to read ERROR for the 3 actual years — Acorn I-REIT's own
disclosed payout ratios (78%/40.5%/34.1%) are genuinely below the CMA's 80% minimum in
those years (a real governance fact carried through from the filings, not a model
defect; see BLUEPRINT.md's "Known simplifications" and research_output.md). Requiring
it there would make `validate_model()` permanently report failure for a legitimately-
correct model, so the overall `ok` verdict only requires the Payout Check for the
*projected* years, where it's a live formula floored at the regulatory minimum in Base.
Balance Sheet / LTV / Income-Producing must hold for every year, actual or projected.
"""
import json
import os

BALANCE_SHEET_TOLERANCE = 0.01


def validate_model(config, results):
    """`results` is a `reit_calculations.build_all(config)`-shaped dict. Returns
    `dict(ok: bool, years: [per-year check dicts])`."""
    bs_ok_series = results["bs"]["balance_check"]
    reg = results["regulatory"]
    payout_pct = results["distributable"]["payout_ratio"]
    payout_min = config.REGULATORY["payout_min"]
    n_actual = len(config.ACTUAL_YEARS)

    years = []
    for i, year in enumerate(config.YEARS):
        is_actual = year in config.ACTUAL_YEARS
        years.append(dict(
            year=year, is_actual=is_actual,
            balance_sheet_ok=bs_ok_series[i],
            ltv_ok=reg["ltv_ok"][i], ltv=reg["ltv"][i], ltv_max=config.REGULATORY["ltv_max"],
            income_producing_ok=reg["income_producing_ok"][i],
            income_producing_pct=reg["income_producing_pct"][i],
            income_producing_min=config.REGULATORY["income_producing_min"],
            payout_ok=reg["payout_ok"][i], payout_pct=payout_pct[i], payout_min=payout_min,
            payout_ok_or_expected=(reg["payout_ok"][i] or is_actual),
        ))

    ok = all(y["balance_sheet_ok"] and y["ltv_ok"] and y["income_producing_ok"] for y in years) and \
        all(y["payout_ok"] for y in years[n_actual:])
    return dict(ok=ok, years=years)


def write_validation_result(config, results, output_dir):
    """Writes `validation_result.json` into `output_dir` (the pipeline's report_workdir/)."""
    validation = validate_model(config, results)
    path = os.path.join(output_dir, "validation_result.json")
    with open(path, "w") as f:
        json.dump(validation, f, indent=2, default=str)
    return path, validation
