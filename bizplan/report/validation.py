"""Pure-Python re-implementation of the Model sheet's "Master Check" section
(bank_excel_renderer.py::_build_master_check) — lets a pipeline gate on model integrity
without a spreadsheet engine. Mirrors the same three checks and tolerances so a workbook
and this validator never disagree about what "OK" means:

- Balance Sheet Check: abs(Assets - Liabilities - Equity) < 0.01
- Capital Adequacy Check: Total Capital / RWA >= CBK minimum
- Liquidity Check: Liquidity Ratio >= CBK statutory minimum

Only covers the projected years (`bank_calculations.build_all()`'s own scope) — the 3
actual years are disclosed facts hardcoded into the renderer from `config.ACTUALS`, not
Python-computed, so there's nothing here to recompute and check for them.
"""
import json
import os

BALANCE_SHEET_TOLERANCE = 0.01


def validate_model(config, results):
    """`results` is a `bank_calculations.build_all(config)`-shaped dict. Returns
    `dict(ok: bool, years: [per-year check dicts])`."""
    bs_check = results["bs"]["check"]
    total_capital_ratio = results["capital"]["total_capital_ratio"]
    total_min = config.CAPITAL["total_capital_rwa_min"]
    liquidity_ratio = results["liquidity"]["ratio"]
    liquidity_min = config.LIQUIDITY_STATUTORY_MIN

    years = []
    for i, year in enumerate(config.YEARS):
        bs_ok = abs(bs_check[i]) < BALANCE_SHEET_TOLERANCE
        capital_ok = total_capital_ratio[i] >= total_min
        liquidity_ok = liquidity_ratio[i] >= liquidity_min
        years.append(dict(
            year=year,
            balance_sheet_ok=bs_ok, balance_sheet_value=bs_check[i],
            capital_adequacy_ok=capital_ok, total_capital_ratio=total_capital_ratio[i],
            total_capital_min=total_min,
            liquidity_ok=liquidity_ok, liquidity_ratio=liquidity_ratio[i],
            liquidity_min=liquidity_min,
        ))

    ok = all(y["balance_sheet_ok"] and y["capital_adequacy_ok"] and y["liquidity_ok"] for y in years)
    return dict(ok=ok, years=years)


def write_validation_result(config, results, output_dir):
    """Writes `validation_result.json` into `output_dir` (the pipeline's report_workdir/)."""
    validation = validate_model(config, results)
    path = os.path.join(output_dir, "validation_result.json")
    with open(path, "w") as f:
        json.dump(validation, f, indent=2, default=str)
    return path, validation
