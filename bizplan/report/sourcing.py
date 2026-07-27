"""Stage 0 of the equity-report pipeline: model sourcing. Given an institution and an
as-of anchor year, produces examples/<institution>/config.py + research_output.md with
ACTUALS = the 3 years ending at the anchor and YEARS = the next 5 years forward, then
deterministically validates and builds the Excel model.

Runs via `claude -p` (see `claude_cli.run_stage`) — subscription-billed, not the raw
Anthropic API the `agent/` module uses. See
.devops/agents/equity-report/model-sourcing.md for the SOP this stage follows (injected
as the system prompt).
"""
from pathlib import Path

from bizplan.report import claude_cli, data as report_data, validation as report_validation

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SOP_PATH = REPO_ROOT / ".devops" / "agents" / "equity-report" / "model-sourcing.md"


def year_windows(as_of):
    actual_years = [as_of - 2, as_of - 1, as_of]
    projection_years = list(range(as_of + 1, as_of + 6))
    return actual_years, projection_years


def _task_prompt(institution, as_of, hints):
    actual_years, projection_years = year_windows(as_of)
    hint_text = "\n".join(f"- {h}" for h in hints) if hints else "(none given — search for them)"
    existing = (REPO_ROOT / "examples" / institution / "config.py").exists()
    scope_note = (
        f"This institution already has examples/{institution}/config.py — read it first "
        f"and determine whether this is a roll-forward or roll-backward re-sourcing "
        f"relative to its current anchor, per SOP section 1."
        if existing else
        "This is a new institution — full onboarding per the SOP, scoped to the "
        "ACTUAL_YEARS window below."
    )
    return (
        f"Follow the model-sourcing SOP above for institution='{institution}', as_of={as_of}.\n\n"
        f"Required ACTUAL_YEARS: {actual_years}\n"
        f"Required projected YEARS: {projection_years}\n\n"
        f"{scope_note}\n\n"
        f"Starting points for finding filings (may be empty):\n{hint_text}\n\n"
        f"Write examples/{institution}/config.py and examples/{institution}/research_output.md "
        f"directly using your file-editing tools. Use real figures only — never fabricate; "
        f"where a figure genuinely isn't disclosed, use a clearly-marked [PLACEHOLDER] and "
        f"note it in research_output.md. Do not run the build or validation yourself — the "
        f"orchestrating script handles that after you finish."
    )


def source_model(institution, as_of, hints):
    task = _task_prompt(institution, as_of, hints)
    claude_cli.run_stage(SOP_PATH, task, cwd=REPO_ROOT)
    _validate_and_build(institution)


def _validate_and_build(institution):
    from bizplan.config_loader import load_and_validate
    from bizplan.financial import bank_calculations, bank_excel_renderer

    config_path = REPO_ROOT / "examples" / institution / "config.py"
    config = load_and_validate(str(config_path))

    computed = report_data.compute(config)
    validation = report_validation.validate_model(config, computed["results"])
    if not validation["ok"]:
        failing = [y for y in validation["years"]
                   if not (y["balance_sheet_ok"] and y["capital_adequacy_ok"] and y["liquidity_ok"])]
        raise RuntimeError(f"Model validation failed for {institution}: {failing}")

    results = bank_calculations.build_all(config)
    output_path = config_path.parent / f"{config.OUTPUT_PREFIX}_Financial_Model.xlsx"
    bank_excel_renderer.build_excel(config, results, str(output_path))
    print(f"Sourced, validated, and built {institution}: {output_path}")
