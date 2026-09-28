# Copyright (c) 2026 Edwin Njeru. Licensed under the MIT License (see LICENSE).

"""Stage 3 of the equity-report pipeline: mechanical earnings-quality / mispricing
pre-decision.

Pure Python arithmetic — no LLM here. This model doesn't build a full Unilever equity
valuation (no DCF/multiples model here — that's out of scope; this project is about the
hyperinflation *accounting* mechanics, not a from-scratch Unilever valuation), so unlike
the REIT pipeline's NAV/DDM/cap-rate blend, this stage computes a materiality flag: how
large is the IAS 29 net monetary gain/(loss) relative to the group's own operating
profit? A large one, if consensus/market commentary treats it as ordinary FX noise
rather than a distinct purchasing-power effect (see config.CONSENSUS's placeholder
note, and Stage 2's job to confirm or correct that against real sell-side commentary),
is exactly the kind of thing that produces a market mispricing this report's job is to
surface. The report-writing stage (section-recommendation.md) combines this flag with
Stage 2's real consensus/price research to argue an actual Buy/Hold/Sell call — this
stage only supplies the mechanical, model-derived half of that argument.

Materiality threshold (10% of group operating profit) is this repo's own documented
judgment call, not a published standard — flagged as such, revisit if it proves too
coarse once tested against real consensus commentary.
"""
import json
import os

MATERIALITY_THRESHOLD = 0.10  # |net monetary gain/loss| / |group operating profit|


def mechanical_recommendation(report_json):
    """`report_json` is `data.to_report_json()`'s output. Returns a dict — see
    `write_recommendation` for the JSON shape written to disk."""
    facts = report_json["company_facts"]
    monetary = facts["net_monetary_gain_loss_eur"]
    op_profit = facts["operating_profit_eur"]
    ratio = abs(monetary) / abs(op_profit) if op_profit else float("inf")
    material = ratio >= MATERIALITY_THRESHOLD

    exposure = report_json["monetary_exposure"]
    worst_subsidiary = min(exposure, key=lambda k: {"A": 4, "B": 3, "C": 2, "D": 1, "F": 0}.get(
        exposure[k]["grade"], -1) if k != "overall_grade" else 99)

    if material:
        signal = "Flag: material"
        rationale = (
            f"Net monetary gain/(loss) of €{monetary:,.0f}m is {ratio * 100:.0f}% of group "
            f"operating profit (€{op_profit:,.0f}m) — above the {MATERIALITY_THRESHOLD * 100:.0f}% "
            f"materiality threshold. {worst_subsidiary.capitalize()} carries the largest "
            f"monetary-exposure grade ({exposure[worst_subsidiary]['grade']}). Unless "
            f"consensus explicitly separates this from ordinary FX translation (see "
            f"config.CONSENSUS / Stage 2 research), reported EPS carries a real, "
            f"non-obvious purchasing-power component that a naive read would miss."
        )
    else:
        signal = "Flag: immaterial"
        rationale = (
            f"Net monetary gain/(loss) of €{monetary:,.0f}m is only {ratio * 100:.0f}% of group "
            f"operating profit (€{op_profit:,.0f}m) — below the {MATERIALITY_THRESHOLD * 100:.0f}% "
            f"materiality threshold this year; the turnover-line restatement effect is larger "
            f"but nets out mostly in cost lines too (see scenario_comparison)."
        )

    return dict(
        net_monetary_gain_loss=monetary, operating_profit=op_profit, ratio=ratio,
        materiality_threshold=MATERIALITY_THRESHOLD, material=material,
        worst_exposure_subsidiary=worst_subsidiary,
        monetary_exposure=exposure, mechanical_signal=signal, rationale=rationale,
    )


def write_recommendation(report_json, output_dir):
    """Writes `recommendation_decision.json` into `output_dir` (the pipeline's
    report_workdir/)."""
    decision = mechanical_recommendation(report_json)
    path = os.path.join(output_dir, "recommendation_decision.json")
    with open(path, "w") as f:
        json.dump(decision, f, indent=2, default=str)
    return path, decision
