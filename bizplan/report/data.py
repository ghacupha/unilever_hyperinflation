"""Serializes `reit_calculations`' valuation/scenario/sensitivity output into the JSON
the equity-research-report pipeline's later (LLM) stages read instead of re-deriving
numbers themselves — the anti-hallucination boundary described in the pipeline plan.
Every figure a report section narrates should trace back to this file's output, not to
a paraphrase invented mid-prompt.

Pure Python, no LLM involved anywhere in this module.
"""
import json
import os

from bizplan.financial import reit_calculations

# Financial Health grade thresholds — this repo's own simple, documented rule (buffer
# above/below the CMA regulatory minimum for LTV/income-producing-%/payout), not a
# Morningstar or CMA-published grading scale. The LLM report stage narrates this
# already-computed grade; it does not assign it. Uses the LATEST ACTUAL year (real
# disclosed data), not a projected year — a "financial health" snapshot should read as
# a statement of present fact, not a forecast.
_LTV_BUFFER_BANDS = (0.15, 0.08, 0.0)          # A/B/C cutoffs, buffer *under* the max; below -> F
_INCOME_PRODUCING_BUFFER_BANDS = (0.15, 0.05, 0.0)  # A/B/C cutoffs, buffer over the minimum; below -> F
_PAYOUT_BUFFER_BANDS = (0.05, 0.0, -0.10)      # A/B/C cutoffs, buffer over the minimum; below -> F
_GRADE_RANK = {"A": 4, "B": 3, "C": 2, "D": 1, "F": 0}
_RANK_GRADE = {v: k for k, v in _GRADE_RANK.items()}


def _buffer_grade(buffer, bands):
    if buffer >= bands[0]:
        return "A"
    if buffer >= bands[1]:
        return "B"
    if buffer >= bands[2]:
        return "C"
    return "F"


def financial_health_grade(ltv, ltv_max, income_producing_pct, income_producing_min,
                           payout_pct, payout_min):
    """Uses the latest ACTUAL year as the current-state snapshot — see module docstring
    for why that's a better choice here than a projected year."""
    ltv_grade = _buffer_grade(ltv_max - ltv, _LTV_BUFFER_BANDS)
    income_producing_grade = _buffer_grade(income_producing_pct - income_producing_min,
                                           _INCOME_PRODUCING_BUFFER_BANDS)
    payout_grade = _buffer_grade(payout_pct - payout_min, _PAYOUT_BUFFER_BANDS)
    overall_rank = min(_GRADE_RANK[ltv_grade], _GRADE_RANK[income_producing_grade],
                        _GRADE_RANK[payout_grade])
    return dict(
        overall_grade=_RANK_GRADE[overall_rank],
        ltv_grade=ltv_grade, ltv=ltv, ltv_max=ltv_max,
        income_producing_grade=income_producing_grade,
        income_producing_pct=income_producing_pct, income_producing_min=income_producing_min,
        payout_grade=payout_grade, payout_pct=payout_pct, payout_min=payout_min,
    )


def company_facts(config):
    """The single authoritative source for company 'hard facts' (total assets/NAV/
    investment property/borrowings/units in issue/NAV per unit) that report-writing
    stages must use instead of re-deriving or pulling from research_output.md's prose.
    Sourced strictly from config.ACTUALS[latest actual year] — the same real-disclosed
    (or clearly-flagged-modeled where undisclosed) figures the rest of the model is
    built on. research_output.md may contain earlier research-process detail, known
    reconciliation gaps, or context — that's for qualitative/business background only
    and must never be treated as authoritative for any figure covered here.
    """
    latest_year = max(config.ACTUAL_YEARS)
    actuals = config.ACTUALS[latest_year]
    return dict(
        as_of_year=latest_year,
        total_assets=actuals["total_assets"],
        investment_property=actuals["investment_property"],
        nav=actuals["nav"],
        nav_per_unit=actuals["nav_per_unit"],
        borrowings=actuals["borrowings"],
        units_in_issue=actuals["units_in_issue"],
    )


def compute(config):
    """Runs the full Python calculation pipeline once. Returns the raw dicts so callers
    (e.g. `validation.validate_model()`) can share this computation instead of each
    re-running `build_all()` themselves."""
    results = reit_calculations.build_all(config)
    scenarios = reit_calculations.build_scenarios(config)
    sensitivity = reit_calculations.build_sensitivity(config)
    return dict(results=results, scenarios=scenarios, sensitivity=sensitivity)


def to_report_json(config, computed):
    """Curates `compute()`'s output into the JSON shape report-writing stages read.

    Unlike the prior banking-model version, no shares-outstanding division is needed
    here — `reit_calculations.build_valuation()`'s NAV/DDM/cap-rate/blended figures are
    already computed per unit (REITs price per unit throughout, not per an
    externally-tracked share count)."""
    results = computed["results"]
    scenarios = computed["scenarios"]
    sensitivity = computed["sensitivity"]

    valuation = results["valuation"]
    valuation_by_scenario = {
        case: {
            "nav_per_unit": scenarios[case]["valuation"]["nav_value"],
            "ddm_per_unit": scenarios[case]["valuation"]["ddm_value"],
            "cap_rate_per_unit": scenarios[case]["valuation"]["cap_rate_value"],
            "blended_per_unit": scenarios[case]["valuation"]["blended_value"],
        }
        for case in ("base", "best", "worst")
    }

    # Latest-actual-year index into the `results` arrays (indexed over config.YEARS,
    # actual+projected combined) -- both `regulatory` and `financial_health` below read
    # off this same index, so "current regulatory standing" always means the same thing
    # in both places rather than one meaning "today" and the other meaning "2030".
    latest_actual_idx = len(config.ACTUAL_YEARS) - 1
    reg = results["regulatory"]

    return dict(
        business_name=config.BUSINESS_NAME,
        currency=config.CURRENCY,
        currency_unit=config.CURRENCY_UNIT_ABBR,
        years=list(config.YEARS),
        company_facts=company_facts(config),
        cost_of_equity=valuation["cost_of_equity"],
        blend_weights=valuation["blend_weights"],
        valuation_per_unit=dict(
            nav=valuation["nav_value"],
            ddm=valuation["ddm_value"],
            cap_rate=valuation["cap_rate_value"],
            peer=valuation["peer_value"],
            blended=valuation["blended_value"],
        ),
        valuation_by_scenario=valuation_by_scenario,
        sensitivity_factors=sensitivity["factors"],
        base_avg_net_profit=sensitivity["base_avg_net_profit"],
        nav_per_unit_series=results["bs"]["nav_per_unit"],
        net_profit_series=results["income_stmt"]["net_profit"],
        regulatory=dict(
            ltv=reg["ltv"][latest_actual_idx], ltv_max=config.REGULATORY["ltv_max"],
            income_producing_pct=reg["income_producing_pct"][latest_actual_idx],
            income_producing_min=config.REGULATORY["income_producing_min"],
            payout_pct=results["distributable"]["payout_ratio"][latest_actual_idx],
            payout_min=config.REGULATORY["payout_min"],
        ),
        peer_reits=list(config.PEER_REITS),
        financial_health=financial_health_grade(
            reg["ltv"][latest_actual_idx], config.REGULATORY["ltv_max"],
            reg["income_producing_pct"][latest_actual_idx], config.REGULATORY["income_producing_min"],
            results["distributable"]["payout_ratio"][latest_actual_idx], config.REGULATORY["payout_min"],
        ),
    )


def write_report_data(config, computed, output_dir):
    """Writes `valuation_inputs.json` into `output_dir` (the pipeline's report_workdir/)."""
    data = to_report_json(config, computed)
    path = os.path.join(output_dir, "valuation_inputs.json")
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)
    return path, data
