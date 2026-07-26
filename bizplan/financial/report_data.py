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


def compute(config):
    """Runs the full Python calculation pipeline once. Returns the raw dicts so callers
    (e.g. `bank_validation.validate_model()`) can share this computation instead of each
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
    )


def write_report_data(config, computed, output_dir):
    """Writes `valuation_inputs.json` into `output_dir` (the pipeline's report_workdir/)."""
    data = to_report_json(config, computed)
    path = os.path.join(output_dir, "valuation_inputs.json")
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)
    return path, data
