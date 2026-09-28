# Copyright (c) 2026 Edwin Njeru. Licensed under the MIT License (see LICENSE).

"""Stage 4 of the equity-report pipeline: per-section report drafting.
See bizplan/report/drafting.py for the actual logic.

    python scripts/draft_report_sections.py <institution> --output-dir <report_workdir> \\
        [--section 07_recommendation]

`--output-dir` must already contain valuation_inputs.json, price_consensus_research.json,
and recommendation_decision.json (Stages 1/2/3's output). `--section` drafts a single
named section only, useful for testing one at a time before running the full batch.
"""
import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from bizplan.report.drafting import SECTIONS, draft_all_sections, draft_section  # noqa: E402


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
