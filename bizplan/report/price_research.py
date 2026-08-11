"""Stage 2 of the equity-report pipeline: price / consensus research.

Given an institution + ticker/exchange and a reference date, researches the current (or,
for a backtest, historical-as-of-that-date) share price and analyst consensus — or a
documented proxy when no real consensus exists — and writes
`<output-dir>/price_consensus_research.json`.

Runs via `claude -p` (see `claude_cli.run_stage`), same subscription-billed convention as
`sourcing.py` — not the raw-API-billed `agent/` module.

`ticker`/`exchange` default to `config.TICKER`/`config.EXCHANGE` when not passed
explicitly — see .devops/agents/equity-report/price-consensus-research.md section 1 for
why `reference_date` must be passed explicitly for a historical backtest rather than
defaulting to today.
"""
import json
from pathlib import Path

from bizplan.report import claude_cli

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SOP_PATH = REPO_ROOT / ".devops" / "agents" / "equity-report" / "price-consensus-research.md"


def _resolve_ticker_exchange(institution, ticker, exchange):
    if ticker and exchange:
        return ticker, exchange
    from bizplan.config_loader import load_and_validate
    config_path = REPO_ROOT / "examples" / institution / "config.py"
    config = load_and_validate(str(config_path))
    ticker = ticker or getattr(config, "TICKER", None)
    exchange = exchange or getattr(config, "EXCHANGE", None)
    if not ticker or not exchange:
        raise RuntimeError(
            f"No ticker/exchange given and config.py for '{institution}' has no "
            f"TICKER/EXCHANGE field — pass --ticker/--exchange explicitly."
        )
    return ticker, exchange


def _task_prompt(institution, ticker, exchange, reference_date, output_path, valuation_inputs_path):
    return (
        f"Follow the price/consensus research SOP above for institution='{institution}' "
        f"(ticker={ticker}, exchange={exchange}).\n\n"
        f"Reference date: {reference_date}\n\n"
        f"Read {valuation_inputs_path} first — its `company_facts` block (NAV per unit, "
        f"total assets, etc.) is this model's own authoritative, already-computed "
        f"figures. If your proxy math needs the institution's NAV per unit, use "
        f"`company_facts.nav_per_unit` from that file — do not independently "
        f"research or derive it from a filing or web source; the model has already "
        f"computed it correctly and consistently with the rest of the report.\n\n"
        f"Write your JSON output to exactly this file path: {output_path}\n\n"
        f"Use your web-search tools directly to find real data (share price, consensus, "
        f"comparable transaction multiples) — do not fabricate."
    )


def research_price_consensus(institution, output_dir, ticker=None, exchange=None, reference_date=None):
    import datetime
    ticker, exchange = _resolve_ticker_exchange(institution, ticker, exchange)
    reference_date = reference_date or datetime.date.today().isoformat()

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "price_consensus_research.json"
    valuation_inputs_path = output_dir / "valuation_inputs.json"

    task = _task_prompt(institution, ticker, exchange, reference_date, output_path, valuation_inputs_path)
    claude_cli.run_stage(SOP_PATH, task, cwd=REPO_ROOT)

    if not output_path.exists():
        raise RuntimeError(f"Expected output not found: {output_path}")
    data = json.loads(output_path.read_text(encoding="utf-8"))
    print(f"Wrote {output_path}")
    return data
