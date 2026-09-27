"""Repeatable refresh: verify/refresh sourcing, then regenerate the Excel model + equity
research report end to end, reusing all existing pipeline code (no new calculation or
rendering logic here — this only orchestrates already-built pieces).

    python scripts/refresh_report.py <institution> [--ticker T --exchange E]
                                      [--reference-date YYYY-MM-DD] [--refresh-sourcing]

Bringing `config.py` up to date before the report runs is opt-in via `--refresh-sourcing`,
which runs Stage 0 (`scripts/source_model.py`'s `source_model()`) to verify/refresh the
config against the institution's real disclosures (see `bizplan/report/sourcing.py`'s
module docstring — this is a verification/refresh pass, not a rolling re-anchor; this
model isn't a multi-year forecast with an as-of year to move). Without it, the update step
is skipped and the report regenerates from `config.py` exactly as it stands — e.g. you
only want fresh price/consensus research without touching the model's calibration.

After the model is up to date, always runs the full equity-report pipeline
(`bizplan.report.pipeline.generate`) — Stage 2's price/consensus research is always
fresh regardless of whether sourcing was refreshed, since market/analyst commentary moves
independently of filings — including the coherence gate (Stage 5.5), into a new
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


def _run_source_model(institution):
    print("=== Verifying/refreshing sourcing (Stage 0: source_model) ===")
    from bizplan.report.sourcing import source_model
    source_model(institution, hints=[])


def refresh(institution, ticker=None, exchange=None, reference_date=None,
            refresh_sourcing=False):
    if refresh_sourcing:
        _run_source_model(institution)

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
    parser.add_argument("--refresh-sourcing", action="store_true",
                         help="Run Stage 0 to verify/refresh config.py against real "
                              "disclosures before regenerating the report")
    args = parser.parse_args()
    refresh(args.institution, ticker=args.ticker, exchange=args.exchange,
            reference_date=args.reference_date, refresh_sourcing=args.refresh_sourcing)


if __name__ == "__main__":
    main()
