"""Repeatable refresh: check for new filings, then regenerate the Excel model + equity
research report end to end, reusing all existing pipeline code (no new calculation or
rendering logic here — this only orchestrates already-built pieces).

    python scripts/refresh_report.py <institution> [--ticker T --exchange E]
                                      [--reference-date YYYY-MM-DD] [--as-of YEAR]
                                      [--skip-update]

Two ways to bring `config.py` up to date before the report runs, mutually exclusive:

- Default (no `--as-of`): runs `agent/cli.py update <institution>` first. That's the
  standalone onboarding/update agent (raw Anthropic API, requires `ANTHROPIC_KEY` in
  `.env` — real per-token cost, separate from the `claude -p` subscription billing the
  report pipeline itself uses) — it checks whether a newer annual/quarterly filing has
  been published and, if so, mechanically rolls `config.py`'s `ACTUALS`/`YEARS` forward.
  If nothing newer is found, or `ANTHROPIC_KEY` isn't set, this step is skipped with a
  warning rather than failing the whole refresh — checking for new filings is a nice-to
  -have on every run, not a hard requirement for regenerating today's report.
- `--as-of YEAR`: instead runs Stage 0 (`scripts/source_model.py`'s `source_model()`),
  which re-anchors `config.py` to an explicit year (roll-forward *or* roll-backward, e.g.
  for a historical backtest) rather than "whatever's newest". Use this when you want a
  specific anchor, not just "the latest available."
- `--skip-update`: skip both of the above and just regenerate the report from
  `config.py` exactly as it stands (e.g. you already ran `agent update` yourself, or you
  only want fresh price/consensus research without touching the model's anchor).

After the model is up to date, always runs the full equity-report pipeline
(`bizplan.report.pipeline.generate`) — Stage 2's price/consensus research is always
fresh regardless of whether a new filing was found, since market price moves daily
independent of filings — including the coherence gate (Stage 5.5), into a new
timestamped `output/<YYYY-MM-DD_HHMMSS>/` folder, matching the launcher convention.

This is the unit intended for scheduling (see the `schedule` skill / a cron-based agent)
so the whole model+report stays current as new information arrives, without a human
re-running each stage by hand.
"""
import argparse
import datetime
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from bizplan.report.pipeline import generate  # noqa: E402


def _run_agent_update(institution):
    """Runs `agent/cli.py update <institution>` as a subprocess (it has its own
    ANTHROPIC_KEY-based client setup, separate from this process). Returns True if it
    ran successfully, False if skipped/failed -- a failure here does not abort the
    refresh, since a fresh report can still be regenerated from the current config.py."""
    print("=== Checking for newer filings (agent update) ===")
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "agent" / "cli.py"), "update", institution],
        cwd=REPO_ROOT, capture_output=True, text=True,
    )
    print(result.stdout)
    if result.returncode != 0:
        print(f"agent update did not complete (exit {result.returncode}); continuing "
              f"the refresh from config.py as it currently stands.\n{result.stderr}",
              file=sys.stderr)
        return False
    return True


def _run_source_model(institution, as_of):
    print(f"=== Re-anchoring to as_of={as_of} (Stage 0: source_model) ===")
    from bizplan.report.sourcing import source_model
    source_model(institution, as_of, hints=[])


def refresh(institution, ticker=None, exchange=None, reference_date=None,
            as_of=None, skip_update=False):
    if not skip_update:
        if as_of is not None:
            _run_source_model(institution, as_of)
        else:
            _run_agent_update(institution)

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    output_dir = REPO_ROOT / "output" / timestamp
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"=== Generating model + report into {output_dir} ===")
    xlsx_path, pdf_path = generate(
        institution, str(output_dir), ticker=ticker, exchange=exchange,
        reference_date=reference_date,
    )
    print(f"\nRefresh complete.\nFinancial model:        {xlsx_path}\n"
          f"Equity research report: {pdf_path}")
    return xlsx_path, pdf_path


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                      formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("institution")
    parser.add_argument("--ticker", default=None, help="Defaults to config.TICKER")
    parser.add_argument("--exchange", default=None, help="Defaults to config.EXCHANGE")
    parser.add_argument("--reference-date", default=None,
                         help="YYYY-MM-DD; defaults to today (see Stage 2's backtest caveat)")
    parser.add_argument("--as-of", type=int, default=None,
                         help="Explicit re-anchor year (Stage 0) instead of agent update's "
                              "'whatever's newest' check")
    parser.add_argument("--skip-update", action="store_true",
                         help="Skip both agent update and Stage 0 -- regenerate the report "
                              "from config.py exactly as it stands")
    args = parser.parse_args()
    refresh(args.institution, ticker=args.ticker, exchange=args.exchange,
            reference_date=args.reference_date, as_of=args.as_of,
            skip_update=args.skip_update)


if __name__ == "__main__":
    main()
