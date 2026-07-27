"""Price / consensus research pipeline stage (Stage 2 of the equity-report pipeline).
See bizplan/report/price_research.py for the actual logic.

    python scripts/research_price_consensus.py <institution> --output-dir <dir> \\
        [--ticker <TICKER> --exchange <EXCHANGE>] [--reference-date YYYY-MM-DD]

`--ticker`/`--exchange` default to `config.TICKER`/`config.EXCHANGE` when omitted.
`--reference-date` defaults to today, which is only correct for a *current*, non-backtest
run — pass it explicitly for a historical backtest (see
.devops/agents/equity-report/price-consensus-research.md section 1).
"""
import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from bizplan.report.price_research import research_price_consensus  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("institution")
    parser.add_argument("--ticker", default=None, help="Defaults to config.TICKER")
    parser.add_argument("--exchange", default=None, help="Defaults to config.EXCHANGE")
    parser.add_argument("--reference-date", default=None,
                         help="YYYY-MM-DD; defaults to today (only correct for a non-backtest run)")
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    research_price_consensus(args.institution, args.output_dir, ticker=args.ticker,
                              exchange=args.exchange, reference_date=args.reference_date)


if __name__ == "__main__":
    main()
