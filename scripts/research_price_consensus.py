"""Price / consensus research pipeline stage (Stage 2 of the equity-report pipeline).

Given an institution + ticker/exchange and a reference date, researches the current (or,
for a backtest, historical-as-of-that-date) share price and analyst consensus — or a
documented proxy when no real consensus exists — and writes
`<output-dir>/price_consensus_research.json`.

Runs via `claude -p` (Claude Code's headless mode, subscription-billed), same convention
as scripts/source_model.py — not the raw-API-billed `agent/` module.

    python scripts/research_price_consensus.py <institution> --ticker <TICKER> \\
        --exchange <EXCHANGE> --output-dir <dir> [--reference-date YYYY-MM-DD]

`--reference-date` defaults to today, which is only correct for a *current*, non-backtest
run — pass it explicitly for a historical backtest (see
.devops/agents/equity-report/price-consensus-research.md section 1).
"""
import argparse
import datetime
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SOP_PATH = REPO_ROOT / ".devops" / "agents" / "equity-report" / "price-consensus-research.md"


def _task_prompt(institution, ticker, exchange, reference_date, output_path):
    return (
        f"Follow the price/consensus research SOP above for institution='{institution}' "
        f"(ticker={ticker}, exchange={exchange}).\n\n"
        f"Reference date: {reference_date}\n\n"
        f"Write your JSON output to exactly this file path: {output_path}\n\n"
        f"Use your web-search tools directly to find real data — do not fabricate."
    )


def research_price_consensus(institution, ticker, exchange, reference_date, output_dir):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "price_consensus_research.json"

    system_prompt = SOP_PATH.read_text(encoding="utf-8")
    task = _task_prompt(institution, ticker, exchange, reference_date, output_path)

    cmd = [
        "claude", "-p",
        "--append-system-prompt", system_prompt,
        "--permission-mode", "bypassPermissions",
        task,
    ]
    result = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        raise RuntimeError(f"claude -p failed for {institution} (exit {result.returncode})")

    if not output_path.exists():
        raise RuntimeError(f"Expected output not found: {output_path}")
    data = json.loads(output_path.read_text(encoding="utf-8"))
    print(f"Wrote {output_path}")
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("institution")
    parser.add_argument("--ticker", required=True)
    parser.add_argument("--exchange", required=True)
    parser.add_argument("--reference-date", default=None,
                         help="YYYY-MM-DD; defaults to today (only correct for a non-backtest run)")
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    reference_date = args.reference_date or datetime.date.today().isoformat()
    research_price_consensus(args.institution, args.ticker, args.exchange,
                              reference_date, args.output_dir)


if __name__ == "__main__":
    main()
