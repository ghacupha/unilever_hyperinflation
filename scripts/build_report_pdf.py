"""Stage 6 CLI: PDF assembly. Pure Python, no LLM.

    python scripts/build_report_pdf.py <institution> --output-dir <report_workdir> \\
        --pdf-path <path/to/output.pdf>

`--output-dir` must already contain valuation_inputs.json, price_consensus_research.json,
recommendation_decision.json (Stages 1/2/3) and report_reviewed.md (Stage 5).
"""
import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from bizplan.financial import report_pdf  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("institution")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--pdf-path", required=True)
    args = parser.parse_args()

    path = report_pdf.build_pdf(args.output_dir, args.pdf_path)
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
