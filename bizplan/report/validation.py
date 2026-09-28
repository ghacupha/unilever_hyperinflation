# Copyright (c) 2026 Edwin Njeru. Licensed under the MIT License (see LICENSE).

"""Pure-Python gate the pipeline runs before anything downstream trusts the numbers.

Unlike the REIT model's Master Check (an independent Balance Sheet / LTV / Income-
Producing / Payout re-derivation that could genuinely disagree with the renderer if
either had a bug), this model's net monetary gain/(loss) is solved as the exact
balancing plug that makes World C's restated balance sheet tie out (see
`hyperinflation_calculations.restate_and_translate`'s docstring) — so a "does the
balance sheet balance" check would be tautologically true by construction, not a real
bug-catcher. The check that *does* have teeth here is calibration fidelity: does the
model's 2024 output still reproduce Unilever's real disclosed 2024 IAS 29 impact
figures within a tight tolerance? If a future edit to config.py's local-currency inputs
broke that (e.g. a typo in one of the solved figures), this catches it. 2025 is a
documented out-of-sample validation, not a pass/fail gate (see
examples/unilever/research_output.md for why total-assets impact structurally can't
flip sign in this model, and why Turkiye's 2025 same-sign match required a margin-
recovery assumption).
"""
import json
import os

CALIBRATION_TOLERANCE_EURM = 0.5


def validate_model(config, results):
    """`results` is a `hyperinflation_calculations.build_model(config)`-shaped dict.
    Returns `dict(ok: bool, primary_year: {...}, validation_year: {...})`."""
    primary_year = min(config.YEARS)
    validation_year = max(config.YEARS)

    calibration = {}
    ok = True
    for name, sub in results[primary_year]["subsidiaries"].items():
        gaps = {}
        for k, v in sub["impact"].items():
            disclosed = config.DISCLOSED_IMPACT_2024[name][k]
            gap = v - disclosed
            within_tolerance = abs(gap) <= CALIBRATION_TOLERANCE_EURM
            gaps[k] = dict(model=v, disclosed=disclosed, gap=gap, within_tolerance=within_tolerance)
            ok = ok and within_tolerance
        calibration[name] = gaps

    return dict(
        ok=ok,
        primary_year=dict(year=primary_year, calibration=calibration),
        validation_year=dict(year=validation_year, gap=results[validation_year]["validation"]),
    )


def write_validation_result(config, results, output_dir):
    """Writes `validation_result.json` into `output_dir` (the pipeline's report_workdir/)."""
    validation = validate_model(config, results)
    path = os.path.join(output_dir, "validation_result.json")
    with open(path, "w") as f:
        json.dump(validation, f, indent=2, default=str)
    return path, validation
