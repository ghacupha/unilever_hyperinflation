# Copyright (c) 2026 Edwin Njeru. Licensed under the MIT License (see LICENSE).

"""Full equity-report pipeline orchestrator: Stages 1 through 6.
See bizplan/report/pipeline.py for the actual logic.

Given an already-onboarded institution (see scripts/source_model.py for Stage 0 —
sourcing a new institution or refreshing an existing one; run that first if needed), this
runs numeric ground-truth extraction + validation, builds the Excel model, researches
price/consensus, computes the mechanical earnings-quality/materiality flag, drafts all
report sections, runs the plagiarism/references review, and assembles the final PDF —
writing both the Financial Model workbook and the Equity Research Report PDF into
--output-dir.

    python scripts/generate_equity_report.py <institution> --output-dir <output/timestamp> \\
        [--ticker <TICKER> --exchange <EXCHANGE>] [--reference-date YYYY-MM-DD]

`--ticker`/`--exchange` default to `config.TICKER`/`config.EXCHANGE` when omitted. The
`claude -p`-based stages (2, 4, 5) are subscription-billed, not separately metered — see
BLUEPRINT.md's "Equity Research Report pipeline" section. This can take a while (each of
those stages is a real research/drafting pass); it is not a quick command.
"""
import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from bizplan.report.pipeline import generate  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("institution")
    parser.add_argument("--ticker", default=None, help="Defaults to config.TICKER")
    parser.add_argument("--exchange", default=None, help="Defaults to config.EXCHANGE")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--reference-date", default=None,
                         help="YYYY-MM-DD; defaults to today (see Stage 2's backtest caveat)")
    args = parser.parse_args()
    generate(args.institution, args.output_dir, ticker=args.ticker, exchange=args.exchange,
              reference_date=args.reference_date)


if __name__ == "__main__":
    main()
