"""Stage 4 of the equity-report pipeline: per-section report drafting.

One `claude -p` call per section (Claude Code's headless mode, subscription-billed —
same convention as scripts/source_model.py and scripts/research_price_consensus.py),
each pointed at the JSON files from Stages 1/2/3 by path rather than having data pasted
into the prompt — keeps prompts small and keeps every number traceable to its source.

    python scripts/draft_report_sections.py <institution> --output-dir <report_workdir> \\
        [--section 07_recommendation]

`--output-dir` must already contain valuation_inputs.json, price_consensus_research.json,
and recommendation_decision.json (Stages 1/2/3's output). `--section` drafts a single
named section only, useful for testing one at a time before running the full batch.
"""
import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
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
    system_prompt = (SOP_DIR / sop_filename).read_text(encoding="utf-8")
    section_md_filename = f"{section_name}.md"
    task = _task_prompt(institution, output_dir, section_md_filename)

    cmd = [
        "claude", "-p",
        "--append-system-prompt", system_prompt,
        "--permission-mode", "bypassPermissions",
        task,
    ]
    result = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
    print(f"--- {section_name} ---")
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        raise RuntimeError(f"claude -p failed for section {section_name} (exit {result.returncode})")

    out_path = Path(output_dir) / "sections" / section_md_filename
    if not out_path.exists():
        raise RuntimeError(f"Expected section output not found: {out_path}")
    return out_path


def draft_all_sections(institution, output_dir):
    (Path(output_dir) / "sections").mkdir(parents=True, exist_ok=True)
    return [draft_section(institution, output_dir, name, sop) for name, sop in SECTIONS]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("institution")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--section", help="Draft only this section (e.g. '07_recommendation')")
    args = parser.parse_args()

    if args.section:
        match = next((s for s in SECTIONS if s[0] == args.section), None)
        if not match:
            raise SystemExit(f"Unknown section '{args.section}'. Options: "
                              f"{', '.join(s[0] for s in SECTIONS)}")
        (Path(args.output_dir) / "sections").mkdir(parents=True, exist_ok=True)
        draft_section(args.institution, args.output_dir, *match)
    else:
        draft_all_sections(args.institution, args.output_dir)


if __name__ == "__main__":
    main()
