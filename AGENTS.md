# AGENTS.md

Index of agent-related resources in this repo.

## Equity Research Report pipeline (all 6 stages built — see BLUEPRINT.md "2026-07-26 (cont.)")

Produces both the Excel financial model and a Morningstar-style equity research PDF. The
engine lives in `bizplan/report/`; `scripts/*.py` are thin CLI wrappers only — parse args,
call into `bizplan.report.*`, print. Every LLM-driven stage runs via `claude -p` (Claude
Code's own headless mode, wrapped by the shared `bizplan/report/claude_cli.py` helper),
authenticated through a Claude subscription rather than a raw `ANTHROPIC_API_KEY` — no
separate per-token billing. Requires the `claude` CLI on `PATH`, logged in normally (never
pass `--bare`, which forces API-key billing).

- **Run the whole thing**: [`scripts/generate_equity_report.py`](scripts/generate_equity_report.py)
  `<institution> --output-dir <dir>` (`--ticker`/`--exchange` optional, default to
  `config.TICKER`/`config.EXCHANGE`), or `REPORT=1 ./scripts/launch.sh <institution>`.
  Takes a while — several `claude -p` round-trips, not a quick command. If a run fails
  partway (e.g. a subscription session-usage limit), check `<output-dir>/report_workdir/`
  first — a stage's output file may already exist and be complete even if the process
  exited non-zero; re-run only the missing stage's script rather than the whole pipeline.
- **Stage 0 — model sourcing** ([SOP](.devops/agents/equity-report/model-sourcing.md),
  `bizplan/report/sourcing.py`, [`scripts/source_model.py`](scripts/source_model.py)):
  handles the institution *and* an as-of anchor year (actuals = the 3 years ending there,
  projections = the next 5 forward). Supports rolling forward (seasonal updates) and
  rolling backward (backtesting a past vantage point).
- **Stage 1/1b — ground truth + validation** (`bizplan/report/data.py`,
  `bizplan/report/validation.py`, pure Python, no LLM): serializes the
  valuation/scenario/sensitivity output and re-implements the Model sheet's Master Check
  so a broken model is caught before any later stage runs.
  `data.financial_health_grade()` also lives here (documented threshold rule).
- **Stage 2 — price/consensus research** ([SOP](.devops/agents/equity-report/price-consensus-research.md),
  `bizplan/report/price_research.py`,
  [`scripts/research_price_consensus.py`](scripts/research_price_consensus.py)): current
  share price + analyst consensus, or a documented proxy (e.g. peer-average P/B) when
  none exists — the realistic case for recently-listed/thinly-covered stocks. Explicit
  reference-date handling so a backtest run can't leak hindsight.
- **Stage 3 — mechanical Buy/Hold/Sell** (`bizplan/report/recommendation.py`, pure
  Python, no LLM): applies Morningstar's real published margin-of-safety bands, scaled
  by an Uncertainty tier derived from this model's own DDM/RI/P-B-ROE spread (this repo's
  own heuristic, documented as such).
- **Stage 4 — per-section drafting** ([SOPs](.devops/agents/equity-report/), 8 files,
  `bizplan/report/drafting.py` — `SECTIONS` is the single source of truth for section
  order, [`scripts/draft_report_sections.py`](scripts/draft_report_sections.py)):
  Investment Thesis, Bulls/Bears, Economic Moat, Valuation/Sensitivity/Scenarios,
  Financial Health, Market Consensus, Recommendation, Risks — each a separate `claude -p`
  call reading the JSON files above by path.
- **Stage 5 — plagiarism/references review** ([SOP](.devops/agents/equity-report/review-plagiarism-references.md),
  `bizplan/report/review.py` (imports its section list from `drafting.py` rather than
  keeping its own copy), [`scripts/review_report.py`](scripts/review_report.py)): one
  whole-document pass — cross-checks every claim, flags (doesn't silently fix)
  errors/inconsistencies, and assembles the References section.
- **Stage 6 — PDF assembly** (`bizplan/report/pdf.py`,
  [`scripts/build_report_pdf.py`](scripts/build_report_pdf.py), pure Python, no LLM):
  ReportLab + matplotlib, no system dependencies.
