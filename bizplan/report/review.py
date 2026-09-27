"""Stage 5 of the equity-report pipeline: plagiarism + references review.

One `claude -p` call over the *whole* assembled draft (all Stage 4 section files plus
the Stage 1/2/3 JSON files) — cross-checks every claim against source (including against
`valuation_inputs.json`'s `company_facts`, the model's own authoritative figures), flags
near-verbatim copying and cross-section contradictions, assembles a deduplicated
References section, and appends the standard Disclaimer.

Writes two separate files, per the SOP's "two files, never mixed" contract:
- `report_reviewed.md` — client-facing document only, no QA commentary.
- `review_findings.json` — a JSON array of unresolved issues (empty if none). The
  coherence gate (`coherence.py`, Stage 5.5) reads this to decide whether to loop.
"""
import json
from pathlib import Path

from bizplan.report import claude_cli
from bizplan.report.drafting import SECTIONS

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SOP_PATH = REPO_ROOT / ".devops" / "agents" / "equity-report" / "review-plagiarism-references.md"

# Derived from drafting.SECTIONS (the single source of truth for section order/filenames)
# rather than a hand-maintained duplicate list.
SECTION_FILES = [f"{name}.md" for name, _ in SECTIONS]


def _task_prompt(institution, output_dir, document_path, findings_path):
    section_list = "\n".join(f"- {output_dir}/sections/{f}" for f in SECTION_FILES)
    return (
        f"Review {institution}'s assembled equity research report per the SOP above.\n\n"
        f"Read these section files, in this order, with your Read tool:\n{section_list}\n\n"
        f"Also read for cross-checking:\n"
        f"- {output_dir}/valuation_inputs.json (company_facts/ias29_impact_primary_year/"
        f"monetary_exposure are the authoritative source for consolidated totals, "
        f"per-subsidiary IAS 29 impact figures, and exposure grades)\n"
        f"- {output_dir}/price_consensus_research.json\n"
        f"- {output_dir}/recommendation_decision.json\n"
        f"- examples/{institution}/research_output.md\n\n"
        f"Write the assembled document (file 1, client-facing only) to exactly this path: "
        f"{document_path}\n\n"
        f"Write the findings array (file 2, per the SOP's JSON shape) to exactly this "
        f"path: {findings_path}"
    )


def review_report(institution, output_dir):
    output_dir = Path(output_dir)
    missing = [f for f in SECTION_FILES if not (output_dir / "sections" / f).exists()]
    if missing:
        raise RuntimeError(f"Missing section file(s), run Stage 4 first: {missing}")

    document_path = output_dir / "report_reviewed.md"
    findings_path = output_dir / "review_findings.json"

    task = _task_prompt(institution, output_dir, document_path, findings_path)
    claude_cli.run_stage(SOP_PATH, task, cwd=REPO_ROOT)

    if not document_path.exists():
        raise RuntimeError(f"Expected output not found: {document_path}")
    if not findings_path.exists():
        raise RuntimeError(f"Expected output not found: {findings_path}")
    findings = json.loads(findings_path.read_text(encoding="utf-8"))
    print(f"Wrote {document_path}")
    print(f"Wrote {findings_path} ({len(findings)} finding(s))")
    return document_path, findings
