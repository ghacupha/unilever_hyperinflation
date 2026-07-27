"""Serializes `bank_calculations`' valuation/scenario/sensitivity output into the JSON
the equity-research-report pipeline's later (LLM) stages read instead of re-deriving
numbers themselves — the anti-hallucination boundary described in the pipeline plan.
Every figure a report section narrates should trace back to this file's output, not to
a paraphrase invented mid-prompt.

Pure Python, no LLM involved anywhere in this module.
"""
import json
import os

from bizplan.financial import bank_calculations

# Financial Health grade thresholds — this repo's own simple, documented rule (buffer
# above the CBK regulatory minimum for capital/liquidity; absolute bands for NPL ratio),
# not a Morningstar or CBK-published grading scale. The LLM report stage narrates this
# already-computed grade; it does not assign it.
_CAPITAL_BUFFER_BANDS = (0.05, 0.02, 0.0)     # A/B/C cutoffs, buffer over minimum; below -> F
_LIQUIDITY_BUFFER_BANDS = (0.15, 0.05, 0.0)   # A/B/C cutoffs, buffer over minimum; below -> F
_NPL_BANDS = (0.05, 0.10, 0.15)               # A/B/C cutoffs, absolute ratio; above -> D
_GRADE_RANK = {"A": 4, "B": 3, "C": 2, "D": 1, "F": 0}
_RANK_GRADE = {v: k for k, v in _GRADE_RANK.items()}


def _buffer_grade(value, minimum, bands):
    buffer = value - minimum
    if buffer >= bands[0]:
        return "A"
    if buffer >= bands[1]:
        return "B"
    if buffer >= bands[2]:
        return "C"
    return "F"


def _npl_grade(npl_ratio):
    if npl_ratio < _NPL_BANDS[0]:
        return "A"
    if npl_ratio < _NPL_BANDS[1]:
        return "B"
    if npl_ratio < _NPL_BANDS[2]:
        return "C"
    return "D"


def financial_health_grade(capital_ratio, capital_min, liquidity_ratio, liquidity_min, npl_ratio):
    """Uses the first projected year (nearest to "now") as the current-state snapshot,
    not a later/terminal projection year."""
    capital_grade = _buffer_grade(capital_ratio, capital_min, _CAPITAL_BUFFER_BANDS)
    liquidity_grade = _buffer_grade(liquidity_ratio, liquidity_min, _LIQUIDITY_BUFFER_BANDS)
    npl_grade = _npl_grade(npl_ratio)
    overall_rank = min(_GRADE_RANK[capital_grade], _GRADE_RANK[liquidity_grade], _GRADE_RANK[npl_grade])
    return dict(
        overall_grade=_RANK_GRADE[overall_rank],
        capital_grade=capital_grade, capital_ratio=capital_ratio, capital_min=capital_min,
        liquidity_grade=liquidity_grade, liquidity_ratio=liquidity_ratio, liquidity_min=liquidity_min,
        npl_grade=npl_grade, npl_ratio=npl_ratio,
    )


def compute(config):
    """Runs the full Python calculation pipeline once. Returns the raw dicts so callers
    (e.g. `validation.validate_model()`) can share this computation instead of each
    re-running `build_all()` themselves."""
    results = bank_calculations.build_all(config)
    scenarios = bank_calculations.build_scenarios(config)
    sensitivity = bank_calculations.build_sensitivity(config)
    return dict(results=results, scenarios=scenarios, sensitivity=sensitivity)


def to_report_json(config, computed):
    """Curates `compute()`'s output into the JSON shape report-writing stages read."""
    results = computed["results"]
    scenarios = computed["scenarios"]
    sensitivity = computed["sensitivity"]
    shares = config.SHARES_OUTSTANDING_2025

    def per_share(equity_value):
        return equity_value / shares

    valuation = results["valuation"]
    valuation_by_scenario = {
        case: {
            "ddm_per_share": per_share(scenarios[case]["valuation"]["ddm_value"]),
            "residual_income_per_share": per_share(scenarios[case]["valuation"]["residual_income_value"]),
            "pb_regression_per_share": per_share(scenarios[case]["valuation"]["pb_regression_value"]),
            "blended_per_share": per_share(scenarios[case]["valuation"]["blended_value"]),
        }
        for case in ("base", "best", "worst")
    }

    return dict(
        business_name=config.BUSINESS_NAME,
        currency=config.CURRENCY,
        currency_unit=config.CURRENCY_UNIT,
        years=list(config.YEARS),
        shares_outstanding_mm=shares,
        cost_of_equity=valuation["cost_of_equity"],
        blend_weights=valuation["blend_weights"],
        valuation_per_share=dict(
            ddm=per_share(valuation["ddm_value"]),
            residual_income=per_share(valuation["residual_income_value"]),
            pb_regression=per_share(valuation["pb_regression_value"]),
            blended=per_share(valuation["blended_value"]),
        ),
        valuation_by_scenario=valuation_by_scenario,
        sensitivity_factors=sensitivity["factors"],
        base_avg_pat=sensitivity["base_avg_pat"],
        roe_series=valuation["roe_series"],
        pat_series=results["income_stmt"]["pat"],
        capital=dict(
            total_capital_ratio=results["capital"]["total_capital_ratio"],
            total_capital_min=config.CAPITAL["total_capital_rwa_min"],
        ),
        liquidity=dict(
            ratio=results["liquidity"]["ratio"],
            min=config.LIQUIDITY_STATUTORY_MIN,
        ),
        npl_ratio=results["loan_book"]["npl_ratio"],
        peer_banks=list(config.PEER_BANKS),
        financial_health=financial_health_grade(
            results["capital"]["total_capital_ratio"][0], config.CAPITAL["total_capital_rwa_min"],
            results["liquidity"]["ratio"][0], config.LIQUIDITY_STATUTORY_MIN,
            results["loan_book"]["npl_ratio"][0],
        ),
    )


def write_report_data(config, computed, output_dir):
    """Writes `valuation_inputs.json` into `output_dir` (the pipeline's report_workdir/)."""
    data = to_report_json(config, computed)
    path = os.path.join(output_dir, "valuation_inputs.json")
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)
    return path, data
