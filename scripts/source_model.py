"""Model-sourcing pipeline stage (Stage 0 of the equity-report pipeline): given an
institution and an as-of anchor year, produces examples/<institution>/config.py +
research_output.md with ACTUALS = the 3 years ending at the anchor and YEARS = the next
5 years forward.

Runs via `claude -p` (Claude Code's headless/print mode), authenticated through the same
Claude subscription as an interactive session — NOT the raw Anthropic API the `agent/`
module uses, so this doesn't cost separate per-token billing. See
.devops/agents/equity-report/model-sourcing.md for the SOP this stage follows (injected
below as the system prompt).

    python scripts/source_model.py <institution> --as-of <year> [hint-url ...]

Requires the `claude` CLI on PATH, authenticated via `claude login` (subscription) —
do not add --bare, which forces raw-API-key billing instead.
"""
import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

SOP_PATH = REPO_ROOT / ".devops" / "agents" / "equity-report" / "model-sourcing.md"


def _year_windows(as_of):
    actual_years = [as_of - 2, as_of - 1, as_of]
    projection_years = list(range(as_of + 1, as_of + 6))
    return actual_years, projection_years


def _task_prompt(institution, as_of, hints):
    actual_years, projection_years = _year_windows(as_of)
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
    system_prompt = SOP_PATH.read_text(encoding="utf-8")
    task = _task_prompt(institution, as_of, hints)

    cmd = [
        "claude", "-p",
        "--append-system-prompt", system_prompt,
        "--permission-mode", "bypassPermissions",
        task,
    ]
    result = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        raise RuntimeError(f"claude -p failed for {institution} (exit {result.returncode})")

    _validate_and_build(institution)


def _validate_and_build(institution):
    from bizplan.config_loader import load_and_validate
    from bizplan.financial import bank_calculations, bank_excel_renderer, bank_validation, report_data

    config_path = REPO_ROOT / "examples" / institution / "config.py"
    config = load_and_validate(str(config_path))

    computed = report_data.compute(config)
    validation = bank_validation.validate_model(config, computed["results"])
    if not validation["ok"]:
        failing = [y for y in validation["years"]
                   if not (y["balance_sheet_ok"] and y["capital_adequacy_ok"] and y["liquidity_ok"])]
        raise RuntimeError(f"Model validation failed for {institution}: {failing}")

    results = bank_calculations.build_all(config)
    output_path = config_path.parent / f"{config.OUTPUT_PREFIX}_Financial_Model.xlsx"
    bank_excel_renderer.build_excel(config, results, str(output_path))
    print(f"Sourced, validated, and built {institution}: {output_path}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("institution", help="Institution folder name, e.g. 'family_bank_kenya'")
    parser.add_argument("--as-of", type=int, required=True,
                         help="Anchor year: actuals are the 3 years ending here, projections are the next 5")
    parser.add_argument("hints", nargs="*", help="Optional starting URLs")
    args = parser.parse_args()
    source_model(args.institution, args.as_of, args.hints)


if __name__ == "__main__":
    main()
