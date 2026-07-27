"""Stage 5 of the equity-report pipeline: plagiarism + references review.
See bizplan/report/review.py for the actual logic.

    python scripts/review_report.py <institution> --output-dir <report_workdir>

`--output-dir` must already contain `sections/*.md` (Stage 4's output) plus
valuation_inputs.json, price_consensus_research.json, recommendation_decision.json
(Stages 1/2/3's output).
"""
import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from bizplan.report.review import review_report  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("institution")
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    review_report(args.institution, args.output_dir)


if __name__ == "__main__":
    main()
