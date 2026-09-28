# Copyright (c) 2026 Edwin Njeru. Licensed under the MIT License (see LICENSE).

"""Stage 0 of the equity-report pipeline: model sourcing/verification. Given an
institution folder name, checks/refreshes examples/<institution>/config.py +
research_output.md against the institution's real disclosed figures, then
deterministically validates and builds the Excel model.

Unlike the prior REIT/bank version, this model isn't a rolling multi-year forecast with
an "as-of anchor year" to re-source each quarter — it's a fixed two-year calibration
(2024, real-disclosed-figure-calibrated) + validation (2025, rolled forward) exercise.
So this stage's job is narrower: verify the existing config's local-currency inputs
still reproduce config.DISCLOSED_IMPACT_2024 (see research_output.md's "Calibration
method"), and refresh citations/figures if Unilever's own disclosures have been
restated or a later annual report has since been filed.

Runs via `claude -p` (see `claude_cli.run_stage`) — subscription-billed, not the raw
Anthropic API the `agent/` module uses. See
.devops/agents/equity-report/model-sourcing.md for the SOP this stage follows (injected
as the system prompt).
"""
from pathlib import Path

from bizplan.report import claude_cli, data as report_data, validation as report_validation

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SOP_PATH = REPO_ROOT / ".devops" / "agents" / "equity-report" / "model-sourcing.md"


def _task_prompt(institution, hints):
    hint_text = "\n".join(f"- {h}" for h in hints) if hints else "(none given — search for them)"
    existing = (REPO_ROOT / "examples" / institution / "config.py").exists()
    scope_note = (
        f"examples/{institution}/config.py already exists — read it and "
        f"research_output.md's 'Calibration method' section first, then verify its "
        f"local-currency subsidiary inputs still reproduce config.DISCLOSED_IMPACT_2024 "
        f"when run through hyperinflation_calculations.build_model(). Only touch a "
        f"figure if Unilever has since restated or re-disclosed it — this is a "
        f"verification/refresh pass, not a re-derivation from scratch."
        if existing else
        "This is a new institution — full onboarding per the SOP."
    )
    return (
        f"Follow the model-sourcing SOP above for institution='{institution}'.\n\n"
        f"{scope_note}\n\n"
        f"Starting points for finding filings (may be empty):\n{hint_text}\n\n"
        f"Write examples/{institution}/config.py and examples/{institution}/research_output.md "
        f"directly using your file-editing tools. Use real figures only — never fabricate; "
        f"where a figure genuinely isn't disclosed, use a clearly-marked [PLACEHOLDER] and "
        f"note it in research_output.md. Do not run the build or validation yourself — the "
        f"orchestrating script handles that after you finish."
    )


def source_model(institution, hints):
    task = _task_prompt(institution, hints)
    claude_cli.run_stage(SOP_PATH, task, cwd=REPO_ROOT)
    _validate_and_build(institution)


def _validate_and_build(institution):
    from bizplan.config_loader import load_and_validate
    from bizplan.financial import hyperinflation_excel_renderer as renderer

    config_path = REPO_ROOT / "examples" / institution / "config.py"
    config = load_and_validate(str(config_path))

    computed = report_data.compute(config)
    validation = report_validation.validate_model(config, computed)
    if not validation["ok"]:
        raise RuntimeError(f"2024 calibration validation failed for {institution}: "
                            f"{validation['primary_year']}")

    output_path = config_path.parent / f"{config.OUTPUT_PREFIX}_Financial_Model.xlsx"
    renderer.build_excel(config, computed, str(output_path))
    print(f"Sourced, validated, and built {institution}: {output_path}")
