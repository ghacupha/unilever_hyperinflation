"""Full equity-report pipeline orchestrator: Stages 1 through 6.

Given an already-onboarded institution (see scripts/source_model.py for Stage 0 —
sourcing a new institution or re-anchoring an existing one to a different as-of period;
run that first if needed), this runs numeric ground-truth extraction + validation,
builds the Excel model, researches price/consensus, computes the mechanical
Buy/Hold/Sell pre-decision, drafts all report sections, runs the plagiarism/references
review, and assembles the final PDF — writing both the Financial Model workbook and the
Equity Research Report PDF into --output-dir.

    python scripts/generate_equity_report.py <institution> --ticker <TICKER> \\
        --exchange <EXCHANGE> --output-dir <output/timestamp> [--reference-date YYYY-MM-DD]

The `claude -p`-based stages (2, 4, 5) are subscription-billed, not separately metered —
see BLUEPRINT.md's "Equity Research Report pipeline" section. This can take a while (each
of those stages is a real research/drafting pass); it is not a quick command.
"""
import argparse
import datetime
import json
import sys
from pathlib import Path
from subprocess import run

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from bizplan.config_loader import load_and_validate  # noqa: E402
from bizplan.financial import (bank_calculations, bank_excel_renderer, bank_validation,  # noqa: E402
                                report_data, report_recommendation, report_pdf)


def _run_stage(args):
    result = run(args, cwd=REPO_ROOT)
    if result.returncode != 0:
        raise RuntimeError(f"Stage failed (exit {result.returncode}): {' '.join(args)}")


def generate(institution, ticker, exchange, output_dir, reference_date=None):
    output_dir = Path(output_dir)
    report_workdir = output_dir / "report_workdir"
    report_workdir.mkdir(parents=True, exist_ok=True)

    config_path = REPO_ROOT / "examples" / institution / "config.py"
    config = load_and_validate(str(config_path))

    print("=== Stage 1/1b: ground truth + validation ===")
    computed = report_data.compute(config)
    validation = bank_validation.validate_model(config, computed["results"])
    if not validation["ok"]:
        raise RuntimeError(f"Model validation failed for {institution}: {validation}")
    _, report_json = report_data.write_report_data(config, computed, str(report_workdir))
    bank_validation.write_validation_result(config, computed["results"], str(report_workdir))

    print("=== Building Excel model ===")
    results = bank_calculations.build_all(config)
    xlsx_path = output_dir / f"{config.OUTPUT_PREFIX}_Financial_Model.xlsx"
    bank_excel_renderer.build_excel(config, results, str(xlsx_path))

    print("=== Stage 2: price/consensus research ===")
    reference_date = reference_date or datetime.date.today().isoformat()
    _run_stage([sys.executable, "scripts/research_price_consensus.py", institution,
                "--ticker", ticker, "--exchange", exchange,
                "--output-dir", str(report_workdir), "--reference-date", reference_date])
    with open(report_workdir / "price_consensus_research.json") as f:
        price_json = json.load(f)

    print("=== Stage 3: mechanical recommendation ===")
    _, decision = report_recommendation.write_recommendation(
        report_json, price_json["share_price"]["value"], str(report_workdir))
    print(f"Mechanical signal: {decision['mechanical_signal']} "
          f"({decision['uncertainty_tier']} uncertainty tier)")

    print("=== Stage 4: drafting report sections ===")
    _run_stage([sys.executable, "scripts/draft_report_sections.py", institution,
                "--output-dir", str(report_workdir)])

    print("=== Stage 5: plagiarism/references review ===")
    _run_stage([sys.executable, "scripts/review_report.py", institution,
                "--output-dir", str(report_workdir)])

    print("=== Stage 6: PDF assembly ===")
    pdf_path = output_dir / f"{config.OUTPUT_PREFIX}_Equity_Research_Report.pdf"
    report_pdf.build_pdf(str(report_workdir), str(pdf_path))

    print(f"\nDone.\nFinancial model:        {xlsx_path}\nEquity research report: {pdf_path}")
    return xlsx_path, pdf_path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("institution")
    parser.add_argument("--ticker", required=True)
    parser.add_argument("--exchange", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--reference-date", default=None,
                         help="YYYY-MM-DD; defaults to today (see Stage 2's backtest caveat)")
    args = parser.parse_args()
    generate(args.institution, args.ticker, args.exchange, args.output_dir, args.reference_date)


if __name__ == "__main__":
    main()
