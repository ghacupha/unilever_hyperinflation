"""Full equity-report pipeline orchestrator: Stages 1 through 6.

Given an already-onboarded institution (see `sourcing.py` for Stage 0 — sourcing a new
institution or re-anchoring an existing one to a different as-of period; run that first
if needed), this runs numeric ground-truth extraction + validation, builds the Excel
model, researches price/consensus, computes the mechanical Buy/Hold/Sell pre-decision,
drafts all report sections, runs the plagiarism/references review, and assembles the
final PDF — writing both the Financial Model workbook and the Equity Research Report PDF
into `output_dir`.

The `claude -p`-based stages (2, 4, 5) are subscription-billed, not separately metered —
see BLUEPRINT.md's "Equity Research Report pipeline" section. This can take a while (each
of those stages is a real research/drafting pass); it is not a quick command.

Calls each stage's function directly in-process (via `sourcing`/`price_research`/
`drafting`/`review`) rather than shelling out to run other scripts as child processes —
each of those stages still shells out to `claude -p` itself where it needs to.
"""
from pathlib import Path

from bizplan.config_loader import load_and_validate
from bizplan.financial import bank_calculations, bank_excel_renderer
from bizplan.report import data as report_data
from bizplan.report import drafting, pdf as report_pdf, price_research, recommendation, review
from bizplan.report import validation as report_validation

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def generate(institution, output_dir, ticker=None, exchange=None, reference_date=None):
    output_dir = Path(output_dir)
    report_workdir = output_dir / "report_workdir"
    report_workdir.mkdir(parents=True, exist_ok=True)

    config_path = REPO_ROOT / "examples" / institution / "config.py"
    config = load_and_validate(str(config_path))

    print("=== Stage 1/1b: ground truth + validation ===")
    computed = report_data.compute(config)
    validation = report_validation.validate_model(config, computed["results"])
    if not validation["ok"]:
        raise RuntimeError(f"Model validation failed for {institution}: {validation}")
    _, report_json = report_data.write_report_data(config, computed, str(report_workdir))
    report_validation.write_validation_result(config, computed["results"], str(report_workdir))

    print("=== Building Excel model ===")
    results = bank_calculations.build_all(config)
    xlsx_path = output_dir / f"{config.OUTPUT_PREFIX}_Financial_Model.xlsx"
    bank_excel_renderer.build_excel(config, results, str(xlsx_path))

    print("=== Stage 2: price/consensus research ===")
    price_json = price_research.research_price_consensus(
        institution, str(report_workdir), ticker=ticker, exchange=exchange,
        reference_date=reference_date)

    print("=== Stage 3: mechanical recommendation ===")
    _, decision = recommendation.write_recommendation(
        report_json, price_json["share_price"]["value"], str(report_workdir))
    print(f"Mechanical signal: {decision['mechanical_signal']} "
          f"({decision['uncertainty_tier']} uncertainty tier)")

    print("=== Stage 4: drafting report sections ===")
    drafting.draft_all_sections(institution, str(report_workdir))

    print("=== Stage 5: plagiarism/references review ===")
    review.review_report(institution, str(report_workdir))

    print("=== Stage 6: PDF assembly ===")
    pdf_path = output_dir / f"{config.OUTPUT_PREFIX}_Equity_Research_Report.pdf"
    report_pdf.build_pdf(str(report_workdir), str(pdf_path))

    print(f"\nDone.\nFinancial model:        {xlsx_path}\nEquity research report: {pdf_path}")
    return xlsx_path, pdf_path
