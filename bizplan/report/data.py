# Copyright (c) 2026 Edwin Njeru. Licensed under the MIT License (see LICENSE).

"""Serializes `hyperinflation_calculations`' output into the JSON the equity-report
pipeline's later (LLM) stages read instead of re-deriving numbers themselves — the
anti-hallucination boundary described in the pipeline plan. Every figure a report
section narrates should trace back to this file's output, not to a paraphrase invented
mid-prompt.

Pure Python, no LLM involved anywhere in this module.
"""
import json
import os

from bizplan.financial import hyperinflation_calculations as calc

# Monetary-exposure grade — this repo's own simple, documented rule: how large a
# subsidiary's net monetary position is relative to its total assets, which is exactly
# the exposure that purchasing-power (IAS 29) or FX-remeasurement (US GAAP temporal)
# gains/losses are driven by. Not a Unilever-published or IFRS-defined grading scale.
_EXPOSURE_BANDS = (0.05, 0.15, 0.30)  # |net monetary position| / total assets cutoffs for A/B/C/D; above -> F
_GRADE_RANK = {"A": 4, "B": 3, "C": 2, "D": 1, "F": 0}
_RANK_GRADE = {v: k for k, v in _GRADE_RANK.items()}


def _exposure_grade(ratio):
    abs_ratio = abs(ratio)
    if abs_ratio <= _EXPOSURE_BANDS[0]:
        return "A"
    if abs_ratio <= _EXPOSURE_BANDS[1]:
        return "B"
    if abs_ratio <= _EXPOSURE_BANDS[2]:
        return "C"
    return "D" if abs_ratio <= 0.5 else "F"


def monetary_exposure_grades(subsidiary_worlds):
    """Grades each subsidiary's net-monetary-position exposure under World C (actual),
    latest year. A low |net monetary position|/total assets ratio means a purchasing-
    power gain/loss barely moves the numbers; a high one means it dominates them."""
    grades = {}
    for name, worlds in subsidiary_worlds.items():
        c = worlds["C"]
        exposure_ratio = c["monetary_gain_loss"] / c["total_assets"] if c["total_assets"] else 0.0
        grades[name] = dict(grade=_exposure_grade(exposure_ratio), exposure_ratio=exposure_ratio,
                             monetary_gain_loss=c["monetary_gain_loss"], total_assets=c["total_assets"])
    overall_rank = min(_GRADE_RANK[g["grade"]] for g in grades.values())
    grades["overall_grade"] = _RANK_GRADE[overall_rank]
    return grades


def company_facts(config):
    """The single authoritative source for 'hard facts' report-writing stages must use
    instead of re-deriving or pulling from research_output.md's prose. Sourced from the
    model's own World-C (actual IFRS) consolidated output for the latest year with a
    real disclosed target, i.e. 2024 -- the calibrated year, not 2025's roll-forward."""
    results = calc.build_model(config)
    year = min(config.YEARS)
    consolidated_c = results[year]["consolidated"]["C"]
    return dict(
        as_of_year=year,
        total_assets_eur=consolidated_c["total_assets"],
        revenue_eur=consolidated_c["revenue"],
        operating_profit_eur=consolidated_c["operating_profit"],
        net_monetary_gain_loss_eur=consolidated_c["monetary_gain_loss"],
        subsidiaries={name: dict(local_currency=sub["local_currency"],
                                  hyperinflationary_since=sub["hyperinflationary_since"])
                      for name, sub in config.SUBSIDIARIES.items()},
    )


def compute(config):
    """Runs the full Python calculation engine once. Returns the raw build_model() dict
    so callers (e.g. `validation.validate_model()`) can share this computation instead
    of each re-running it themselves."""
    return calc.build_model(config)


def to_report_json(config, computed):
    """Curates `compute()`'s output into the JSON shape report-writing stages read."""
    primary_year = min(config.YEARS)
    latest_year = max(config.YEARS)
    primary = computed[primary_year]
    latest = computed[latest_year]

    ias29_impact = {name: sub["impact"] for name, sub in primary["subsidiaries"].items()}
    validation_gap = latest["validation"]

    return dict(
        business_name=config.BUSINESS_NAME,
        currency=config.CURRENCY,
        currency_unit=config.CURRENCY_UNIT_ABBR,
        years=list(config.YEARS),
        company_facts=company_facts(config),
        ias29_impact_primary_year=dict(year=primary_year, by_subsidiary=ias29_impact),
        scenario_comparison=primary["comparison"],
        validation_gap=dict(year=latest_year, by_subsidiary=validation_gap),
        monetary_exposure=monetary_exposure_grades(
            {n: s["worlds"] for n, s in primary["subsidiaries"].items()}),
        consensus=dict(config.CONSENSUS),
        valuation=dict(config.VALUATION),
        peer_comparison=dict(getattr(config, "PEER_COMPARISON", {})),
        standard_setting_note=dict(getattr(config, "STANDARD_SETTING_NOTE", {})),
    )


def write_report_data(config, computed, output_dir):
    """Writes `valuation_inputs.json` into `output_dir` (the pipeline's report_workdir/)."""
    data = to_report_json(config, computed)
    path = os.path.join(output_dir, "valuation_inputs.json")
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)
    return path, data
