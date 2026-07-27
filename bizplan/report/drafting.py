"""Stage 4 of the equity-report pipeline: per-section report drafting.

One `claude -p` call per section (see `claude_cli.run_stage`), each pointed at the JSON
files from Stages 1/2/3 by path rather than having data pasted into the prompt — keeps
prompts small and keeps every number traceable to its source.

`SECTIONS` is this pipeline's single source of truth for the report's section order —
`review.py` imports it directly rather than keeping its own separate copy.
"""
from pathlib import Path

from bizplan.report import claude_cli

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SOP_DIR = REPO_ROOT / ".devops" / "agents" / "equity-report"

# (section filename stem, SOP filename) — order is the report's own section order.
SECTIONS = [
    ("01_investment_thesis", "section-investment-thesis.md"),
    ("02_bulls_bears", "section-bulls-bears.md"),
    ("03_economic_moat", "section-economic-moat.md"),
    ("04_valuation_scenarios", "section-valuation-scenarios.md"),
    ("05_financial_health", "section-financial-health.md"),
    ("06_market_consensus", "section-market-consensus.md"),
    ("07_recommendation", "section-recommendation.md"),
    ("08_risks_uncertainty", "section-risks-uncertainty.md"),
]


def _task_prompt(institution, output_dir, section_md_filename):
    return (
        f"Write this section for {institution}'s equity research report.\n\n"
        f"Read these files directly with your Read tool for ground truth — do not ask "
        f"for them to be pasted:\n"
        f"- {output_dir}/valuation_inputs.json\n"
        f"- {output_dir}/price_consensus_research.json\n"
        f"- {output_dir}/recommendation_decision.json\n"
        f"- examples/{institution}/research_output.md (business/company context)\n\n"
        f"Write your markdown output to exactly this file path: "
        f"{output_dir}/sections/{section_md_filename}\n\n"
        f"Do not fabricate any number — every figure must trace back to one of the JSON "
        f"files above."
    )


def draft_section(institution, output_dir, section_name, sop_filename):
    section_md_filename = f"{section_name}.md"
    task = _task_prompt(institution, output_dir, section_md_filename)

    print(f"--- {section_name} ---")
    claude_cli.run_stage(SOP_DIR / sop_filename, task, cwd=REPO_ROOT)

    out_path = Path(output_dir) / "sections" / section_md_filename
    if not out_path.exists():
        raise RuntimeError(f"Expected section output not found: {out_path}")
    return out_path


def draft_all_sections(institution, output_dir):
    (Path(output_dir) / "sections").mkdir(parents=True, exist_ok=True)
    return [draft_section(institution, output_dir, name, sop) for name, sop in SECTIONS]
