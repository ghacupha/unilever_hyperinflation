"""Stage 5 of the equity-report pipeline: plagiarism + references review.

One `claude -p` call over the *whole* assembled draft (all Stage 4 section files plus
the Stage 1/2/3 JSON files) — cross-checks every claim against source, flags
near-verbatim copying and cross-section contradictions, assembles a deduplicated
References section, and appends the standard Disclaimer. Writes `report_reviewed.md`.
"""
from pathlib import Path

from bizplan.report import claude_cli
from bizplan.report.drafting import SECTIONS

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SOP_PATH = REPO_ROOT / ".devops" / "agents" / "equity-report" / "review-plagiarism-references.md"

# Derived from drafting.SECTIONS (the single source of truth for section order/filenames)
# rather than a hand-maintained duplicate list.
SECTION_FILES = [f"{name}.md" for name, _ in SECTIONS]


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

    task = _task_prompt(institution, output_dir)
    claude_cli.run_stage(SOP_PATH, task, cwd=REPO_ROOT)

    out_path = output_dir / "report_reviewed.md"
    if not out_path.exists():
        raise RuntimeError(f"Expected output not found: {out_path}")
    print(f"Wrote {out_path}")
    return out_path
