"""Stage 5 of the equity-report pipeline: plagiarism + references review.

One `claude -p` call over the *whole* assembled draft (all Stage 4 section files plus
the Stage 1/2/3 JSON files) — cross-checks every claim against source, flags
near-verbatim copying and cross-section contradictions, assembles a deduplicated
References section, and appends the standard Disclaimer. Writes `report_reviewed.md`.

Same `claude -p` subscription-billed convention as the earlier stages.

    python scripts/review_report.py <institution> --output-dir <report_workdir>

`--output-dir` must already contain `sections/*.md` (Stage 4's output) plus
valuation_inputs.json, price_consensus_research.json, recommendation_decision.json
(Stages 1/2/3's output).
"""
import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SOP_PATH = REPO_ROOT / ".devops" / "agents" / "equity-report" / "review-plagiarism-references.md"

# Must match scripts/draft_report_sections.py's SECTIONS order.
SECTION_FILES = [
    "01_investment_thesis.md", "02_bulls_bears.md", "03_economic_moat.md",
    "04_valuation_scenarios.md", "05_financial_health.md", "06_market_consensus.md",
    "07_recommendation.md", "08_risks_uncertainty.md",
]


def _task_prompt(institution, output_dir):
    section_list = "\n".join(f"- {output_dir}/sections/{f}" for f in SECTION_FILES)
    return (
        f"Review {institution}'s assembled equity research report per the SOP above.\n\n"
        f"Read these section files, in this order, with your Read tool:\n{section_list}\n\n"
        f"Also read for cross-checking:\n"
        f"- {output_dir}/valuation_inputs.json\n"
        f"- {output_dir}/price_consensus_research.json\n"
        f"- {output_dir}/recommendation_decision.json\n"
        f"- examples/{institution}/research_output.md\n\n"
        f"Write the final assembled document to exactly this file path: "
        f"{output_dir}/report_reviewed.md"
    )


def review_report(institution, output_dir):
    output_dir = Path(output_dir)
    missing = [f for f in SECTION_FILES if not (output_dir / "sections" / f).exists()]
    if missing:
        raise RuntimeError(f"Missing section file(s), run Stage 4 first: {missing}")

    system_prompt = SOP_PATH.read_text(encoding="utf-8")
    task = _task_prompt(institution, output_dir)

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
        raise RuntimeError(f"claude -p failed for review stage (exit {result.returncode})")

    out_path = output_dir / "report_reviewed.md"
    if not out_path.exists():
        raise RuntimeError(f"Expected output not found: {out_path}")
    print(f"Wrote {out_path}")
    return out_path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("institution")
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    review_report(args.institution, args.output_dir)


if __name__ == "__main__":
    main()
