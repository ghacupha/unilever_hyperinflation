"""Stage 5.5 of the equity-report pipeline: the coherence gate.

An evaluator-optimizer loop (Stage 5's review as evaluator, a targeted correction pass as
optimizer) that runs between drafting/review and PDF assembly. Bounded by
`max_iterations` -- LLMs cannot reliably self-correct without external grounding, so each
iteration re-runs Stage 5 fresh against the *current* section files rather than trusting
the correction pass's own claim that it fixed things.

The JSON ground truth (`valuation_inputs.json` -- especially its `company_facts` block --
`price_consensus_research.json`, `recommendation_decision.json`) is always authoritative;
corrections conform report *text* to that ground truth, never the reverse, and the Excel
model itself is never touched here. No external data is re-fetched during the loop: every
finding this stage can act on is a text-vs-already-fetched-ground-truth mismatch, not a
missing-research gap (see BLUEPRINT.md's coherence-gate entry for why).

If the loop exhausts `max_iterations` without reaching zero findings, returns `ok=False`
with the last known findings so the caller (`pipeline.py`) can still assemble the PDF, with
a visible "Unresolved QA Flags" appendix, rather than silently shipping unresolved issues
or blocking forever.
"""
from pathlib import Path

from bizplan.report import claude_cli, review

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SOP_PATH = REPO_ROOT / ".devops" / "agents" / "equity-report" / "coherence-apply-fixes.md"

DEFAULT_MAX_ITERATIONS = 10


def _apply_fixes_task_prompt(institution, output_dir, findings_path):
    return (
        f"Apply fixes for {institution}'s equity research report per the SOP above.\n\n"
        f"Read the findings at: {findings_path}\n\n"
        f"For each finding, fix only the named section file under {output_dir}/sections/ "
        f"(e.g. a finding with section='01_investment_thesis' means "
        f"{output_dir}/sections/01_investment_thesis.md).\n\n"
        f"Ground truth, always authoritative over report prose: "
        f"{output_dir}/valuation_inputs.json (especially its company_facts block), "
        f"{output_dir}/price_consensus_research.json, and "
        f"{output_dir}/recommendation_decision.json. Never treat research_output.md as "
        f"authoritative over these -- if a finding says a section contradicts one of these "
        f"JSON files, the JSON file is right and the section text is wrong.\n\n"
        f"Do not use any web-search or network tool. All data needed to fix these findings "
        f"already exists in the JSON files above -- this stage corrects report text to "
        f"match already-fetched ground truth, it does not re-research anything.\n\n"
        f"Edit the section file(s) directly with your Edit tool. Do not modify the JSON "
        f"files, research_output.md, config.py, or the Excel model -- those are the ground "
        f"truth these fixes conform to, never the reverse."
    )


def _apply_fixes(institution, output_dir, findings_path):
    task = _apply_fixes_task_prompt(institution, output_dir, findings_path)
    claude_cli.run_stage(SOP_PATH, task, cwd=REPO_ROOT)


def run_coherence_gate(institution, output_dir, max_iterations=DEFAULT_MAX_ITERATIONS):
    """Stage 5 (evaluator) + a targeted correction pass (optimizer), looped until
    `review_findings.json` comes back empty or `max_iterations` evaluation passes are
    exhausted. Returns `{"ok": bool, "iterations": int, "findings": [...]}`."""
    output_dir = Path(output_dir)
    findings_path = output_dir / "review_findings.json"

    findings = []
    for iteration in range(1, max_iterations + 1):
        print(f"=== Stage 5.5: coherence gate, iteration {iteration}/{max_iterations} ===")
        _, findings = review.review_report(institution, str(output_dir))
        if not findings:
            return dict(ok=True, iterations=iteration, findings=[])
        if iteration == max_iterations:
            break
        print(f"{len(findings)} finding(s) -- applying fixes and re-reviewing")
        _apply_fixes(institution, str(output_dir), findings_path)

    print(f"Coherence gate did not converge after {max_iterations} iterations "
          f"({len(findings)} finding(s) remain) -- proceeding with a QA-flags appendix.")
    return dict(ok=False, iterations=max_iterations, findings=findings)
