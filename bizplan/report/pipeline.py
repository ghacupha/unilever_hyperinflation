# Copyright (c) 2026 Edwin Njeru. Licensed under the MIT License (see LICENSE).

"""Full equity-report pipeline orchestrator: Stages 1 through 6, plus Stage 5.5.

Given an already-onboarded institution (see `sourcing.py` for Stage 0 — sourcing a new
institution or re-anchoring an existing one to a different as-of period; run that first
if needed), this runs numeric ground-truth extraction + validation, builds the Excel
model, researches price/consensus, computes the mechanical Buy/Hold/Sell pre-decision,
drafts all report sections, runs the plagiarism/references review, runs the coherence
gate (Stage 5.5 — an evaluator-optimizer loop that re-checks and fixes report-vs-model
mismatches before anything ships), and assembles the final PDF — writing both the
Financial Model workbook and the Equity Research Report PDF into `output_dir`.

The `claude -p`-based stages (2, 4, 5, 5.5) are subscription-billed, not separately
metered — see BLUEPRINT.md's "Equity Research Report pipeline" section. This can take a
while (each of those stages is a real research/drafting pass, and 5.5 can re-run Stage 5
up to `COHERENCE_MAX_ITERATIONS` times); it is not a quick command.

Calls each stage's function directly in-process (via `sourcing`/`price_research`/
`drafting`/`review`/`coherence`) rather than shelling out to run other scripts as child
processes — each of those stages still shells out to `claude -p` itself where it needs to.
"""
from pathlib import Path

from bizplan.config_loader import load_and_validate
from bizplan.financial import hyperinflation_excel_renderer as renderer
from bizplan.report import coherence, data as report_data
from bizplan.report import drafting, pdf as report_pdf, price_research, recommendation
from bizplan.report import validation as report_validation

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# Bounded per the user's own reliability decision (2026-07-27 coherence-gate review): the
# gate blocks export while it loops, never re-fetches external data mid-loop (findings are
# text-vs-already-fetched-ground-truth mismatches, not missing research), and after this
# many non-converging iterations ships anyway with a visible "Unresolved QA Flags"
# appendix rather than blocking forever.
COHERENCE_MAX_ITERATIONS = coherence.DEFAULT_MAX_ITERATIONS


def generate(institution, output_dir, ticker=None, exchange=None, reference_date=None):
    output_dir = Path(output_dir)
    report_workdir = output_dir / "report_workdir"
    report_workdir.mkdir(parents=True, exist_ok=True)

    config_path = REPO_ROOT / "examples" / institution / "config.py"
    config = load_and_validate(str(config_path))

    print("=== Stage 1/1b: ground truth + validation ===")
    computed = report_data.compute(config)
    validation = report_validation.validate_model(config, computed)
    if not validation["ok"]:
        raise RuntimeError(f"2024 calibration validation failed for {institution}: "
                            f"{validation['primary_year']}")
    _, report_json = report_data.write_report_data(config, computed, str(report_workdir))
    report_validation.write_validation_result(config, computed, str(report_workdir))

    print("=== Building Excel model ===")
    xlsx_path = output_dir / f"{config.OUTPUT_PREFIX}_Financial_Model.xlsx"
    renderer.build_excel(config, computed, str(xlsx_path))

    print("=== Stage 2: price/consensus research ===")
    price_research.research_price_consensus(
        institution, str(report_workdir), ticker=ticker, exchange=exchange,
        reference_date=reference_date)

    print("=== Stage 3: mechanical earnings-quality flag ===")
    _, decision = recommendation.write_recommendation(report_json, str(report_workdir))
    print(f"Mechanical signal: {decision['mechanical_signal']}")

    print("=== Stage 4: drafting report sections ===")
    drafting.draft_all_sections(institution, str(report_workdir))

    print("=== Stage 5 + 5.5: plagiarism/references review + coherence gate ===")
    gate_result = coherence.run_coherence_gate(
        institution, str(report_workdir), max_iterations=COHERENCE_MAX_ITERATIONS)
    if gate_result["ok"]:
        print(f"Coherence gate converged after {gate_result['iterations']} iteration(s), "
              f"0 unresolved findings.")
    else:
        print(f"Coherence gate did NOT converge after {gate_result['iterations']} "
              f"iteration(s) — {len(gate_result['findings'])} finding(s) will ship as a "
              f"visible QA-flags appendix instead of blocking the export.")

    print("=== Stage 6: PDF assembly ===")
    pdf_path = output_dir / f"{config.OUTPUT_PREFIX}_Equity_Research_Report.pdf"
    report_pdf.build_pdf(str(report_workdir), str(pdf_path),
                          unresolved_findings=gate_result["findings"])

    print(f"\nDone.\nFinancial model:        {xlsx_path}\nEquity research report: {pdf_path}")
    return xlsx_path, pdf_path
