"""Repeatable refresh: check for new filings, then regenerate the Excel model + equity
research report end to end, reusing all existing pipeline code (no new calculation or
rendering logic here — this only orchestrates already-built pieces).

    python scripts/refresh_report.py <institution> [--ticker T --exchange E]
                                      [--reference-date YYYY-MM-DD] [--as-of YEAR]
                                      [--skip-update]

Bringing `config.py` up to date before the report runs is opt-in via `--as-of YEAR`,
which runs Stage 0 (`scripts/source_model.py`'s `source_model()`) to re-anchor `config.py`
to an explicit year (roll-forward *or* roll-backward, e.g. for a historical backtest).
Without `--as-of`, the update step is skipped and the report regenerates from `config.py`
exactly as it stands — e.g. you only want fresh price/consensus research without touching
the model's anchor. `--skip-update` is equivalent to omitting `--as-of` and exists for
explicitness in scripts/cron jobs.

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
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from bizplan.report.pipeline import generate  # noqa: E402


def _run_source_model(institution, as_of):
    print(f"=== Re-anchoring to as_of={as_of} (Stage 0: source_model) ===")
    from bizplan.report.sourcing import source_model
    source_model(institution, as_of, hints=[])


def refresh(institution, ticker=None, exchange=None, reference_date=None,
            as_of=None, skip_update=False):
    if not skip_update and as_of is not None:
        _run_source_model(institution, as_of)

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
                         help="Explicit re-anchor year (Stage 0); omit to leave config.py's "
                              "anchor untouched")
    parser.add_argument("--skip-update", action="store_true",
                         help="Equivalent to omitting --as-of -- regenerate the report "
                              "from config.py exactly as it stands")
    args = parser.parse_args()
    refresh(args.institution, ticker=args.ticker, exchange=args.exchange,
            reference_date=args.reference_date, as_of=args.as_of,
            skip_update=args.skip_update)


if __name__ == "__main__":
    main()
