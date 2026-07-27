# AGENTS.md

Index of agent-related resources in this repo.

## Bank/financial-institution onboarding

- **SOP**: [`.devops/agents/bank-onboarding.md`](.devops/agents/bank-onboarding.md) —
  the institution-agnostic playbook (data intake, extraction, known pitfalls,
  `config.py` schema, verification, seasonal updates).
- **Runnable agent**: [`agent/`](agent/) — a standalone Python program that
  executes the SOP: researches a new institution's public filings (Anthropic
  API, server-side web search + native PDF reading), writes
  `examples/<institution>/config.py` and `research_output.md`, runs the
  existing renderer, and can be re-run later (`update`) to ingest new
  annual/quarterly filings and roll the model forward. See `agent/cli.py`
  for usage. Requires `ANTHROPIC_API_KEY`; each run costs real API tokens.

## Equity Research Report pipeline (all 6 stages built — see BLUEPRINT.md "2026-07-26 (cont.)")

Produces both the Excel financial model and a Morningstar-style equity research PDF.
Every LLM-driven stage runs via `claude -p` (Claude Code's own headless mode),
authenticated through a Claude subscription rather than a raw `ANTHROPIC_API_KEY` — no
separate per-token billing, unlike `agent/` above. Requires the `claude` CLI on `PATH`,
logged in normally (never pass `--bare`, which forces API-key billing).

- **Run the whole thing**: [`scripts/generate_equity_report.py`](scripts/generate_equity_report.py)
  `<institution> --ticker <TICKER> --exchange <EXCHANGE> --output-dir <dir>`, or
  `REPORT=1 TICKER=<TICKER> EXCHANGE=<EXCHANGE> ./scripts/launch.sh <institution>`. Takes
  a while — several `claude -p` round-trips, not a quick command. If a run fails partway
  (e.g. a subscription session-usage limit), check `<output-dir>/report_workdir/` first —
  a stage's output file may already exist and be complete even if the process exited
  non-zero; re-run only the missing stage's script rather than the whole pipeline.
- **Stage 0 — model sourcing** ([SOP](.devops/agents/equity-report/model-sourcing.md),
  [`scripts/source_model.py`](scripts/source_model.py)): generalizes `bank-onboarding.md`
  along a second axis — institution *and* an as-of anchor year (actuals = the 3 years
  ending there, projections = the next 5 forward). Supports rolling forward (seasonal
  updates) and rolling backward (backtesting a past vantage point). Not run by
  `generate_equity_report.py` automatically — run it first if the institution needs
  onboarding or re-anchoring.
- **Stage 1/1b — ground truth + validation** (`bizplan/financial/report_data.py`,
  `bizplan/financial/bank_validation.py`, pure Python, no LLM): serializes the
  valuation/scenario/sensitivity output and re-implements the Model sheet's Master Check
  so a broken model is caught before any later stage runs.
  `report_data.financial_health_grade()` also lives here (documented threshold rule).
- **Stage 2 — price/consensus research** ([SOP](.devops/agents/equity-report/price-consensus-research.md),
  [`scripts/research_price_consensus.py`](scripts/research_price_consensus.py)): current
  share price + analyst consensus, or a documented proxy (e.g. peer-average P/B) when
  none exists — the realistic case for recently-listed/thinly-covered stocks. Explicit
  reference-date handling so a backtest run can't leak hindsight.
- **Stage 3 — mechanical Buy/Hold/Sell** (`bizplan/financial/report_recommendation.py`,
  pure Python, no LLM): applies Morningstar's real published margin-of-safety bands,
  scaled by an Uncertainty tier derived from this model's own DDM/RI/P-B-ROE spread (this
  repo's own heuristic, documented as such).
- **Stage 4 — per-section drafting** ([SOPs](.devops/agents/equity-report/), 8 files,
  [`scripts/draft_report_sections.py`](scripts/draft_report_sections.py)): Investment
  Thesis, Bulls/Bears, Economic Moat, Valuation/Sensitivity/Scenarios, Financial Health,
  Market Consensus, Recommendation, Risks — each a separate `claude -p` call reading the
  JSON files above by path.
- **Stage 5 — plagiarism/references review** ([SOP](.devops/agents/equity-report/review-plagiarism-references.md),
  [`scripts/review_report.py`](scripts/review_report.py)): one whole-document pass —
  cross-checks every claim, flags (doesn't silently fix) errors/inconsistencies, and
  assembles the References section.
- **Stage 6 — PDF assembly** (`bizplan/financial/report_pdf.py`,
  [`scripts/build_report_pdf.py`](scripts/build_report_pdf.py), pure Python, no LLM):
  ReportLab + matplotlib, no system dependencies.
