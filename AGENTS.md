# AGENTS.md

Index of agent-related resources in this repo.

## Equity Research Report pipeline (adapted to the hyperinflation-accounting domain, 2026-09-27)

Produces both the Excel financial model and a Morningstar-style equity research PDF. The
engine lives in `bizplan/report/`; `scripts/*.py` are thin CLI wrappers only — parse args,
call into `bizplan.report.*`, print. Every LLM-driven stage runs via `claude -p` (Claude
Code's own headless mode, wrapped by the shared `bizplan/report/claude_cli.py` helper),
authenticated through a Claude subscription rather than a raw `ANTHROPIC_API_KEY` — no
separate per-token billing. Requires the `claude` CLI on `PATH`, logged in normally (never
pass `--bare`, which forces API-key billing).

**Verification status**: the deterministic (non-LLM) stages — 1, 1b, 3, 6 — have been
verified end-to-end against the calibrated `unilever` instance (see `BACKLOG.md` Phase 3):
the JSON ground truth, the calibration-fidelity validator, the mechanical
earnings-quality flag, and PDF assembly all produce correct output (confirmed with a real
generated PDF and cross-checked Excel formulas via the `formulas` package). The
`claude -p`-driven stages (2, 4, 5, 5.5) have now had a full live run too (see
`BACKLOG.md` Phase 4, 2026-09-27) — real Stage 2 web research, all 8 Stage 4 sections
drafted, and the Stage 5.5 coherence gate converged after 5 iterations to 0 unresolved
findings, producing a real PDF in `output/2026-09-27_142024/`. Stage 0 (sourcing) hasn't
been re-run since `unilever` was already onboarded going into that run.

- **Run the whole thing**: [`scripts/generate_equity_report.py`](scripts/generate_equity_report.py)
  `<institution> --output-dir <dir>` (`--ticker`/`--exchange` optional, default to
  `config.TICKER`/`config.EXCHANGE`), or `REPORT=1 ./scripts/launch.sh <institution>`.
  Takes a while — several `claude -p` round-trips, not a quick command. If a run fails
  partway (e.g. a subscription session-usage limit), check `<output-dir>/report_workdir/`
  first — a stage's output file may already exist and be complete even if the process
  exited non-zero; re-run only the missing stage's script rather than the whole pipeline.
- **Stage 0 — model sourcing** ([SOP](.devops/agents/equity-report/model-sourcing.md),
  `bizplan/report/sourcing.py`, [`scripts/source_model.py`](scripts/source_model.py)):
  verifies/refreshes an institution's `config.py` against its real disclosed IAS 29
  impact figures. Unlike the prior REIT/bank pipeline, this is **not** a rolling
  multi-year forecast with an as-of anchor to re-source each quarter — it's a fixed
  two-year calibration (primary year) + validation (roll-forward year) exercise, so this
  stage's job is narrower: confirm the config still reproduces
  `config.DISCLOSED_IMPACT_2024` and refresh citations if the institution has since
  restated a figure.
- **Stage 1/1b — ground truth + validation** (`bizplan/report/data.py`,
  `bizplan/report/validation.py`, pure Python, no LLM): serializes the World A/B/C
  scenario comparison, per-subsidiary IAS 29 impact, and monetary-exposure grades, and
  gates on **calibration fidelity** — does the model's primary-year output still
  reproduce the institution's real disclosed impact figures within tolerance? (Not a
  Balance Sheet Check the way the REIT model had one — this model's net monetary
  gain/(loss) is solved as the exact balancing plug by construction, so a balance check
  would be tautological; see `validation.py`'s module docstring for why calibration
  fidelity is the check that actually has teeth here.)
- **Stage 2 — price/consensus research** ([SOP](.devops/agents/equity-report/price-consensus-research.md),
  `bizplan/report/price_research.py`,
  [`scripts/research_price_consensus.py`](scripts/research_price_consensus.py)): current
  share price + analyst consensus — specifically researching whether real sell-side
  commentary distinguishes the IAS 29 net monetary gain/(loss) from ordinary FX
  translation, or folds it into generic "FX headwind" noise (the market-perception
  question this whole report is built around). Explicit reference-date handling so a
  backtest run can't leak hindsight.
- **Stage 3 — mechanical earnings-quality flag** (`bizplan/report/recommendation.py`,
  pure Python, no LLM): flags whether the net monetary gain/(loss) is material relative
  to group operating profit (a documented 10% threshold, this repo's own heuristic — not
  a Buy/Hold/Sell price-vs-fair-value call the way the REIT pipeline had, since this
  model doesn't build a full equity valuation). The Recommendation section (Stage 4)
  combines this flag with Stage 2's real consensus research to argue an actual
  Buy/Hold/Sell-style call about earnings-quality mispricing specifically.
- **Stage 4 — per-section drafting** ([SOPs](.devops/agents/equity-report/), 8 files,
  `bizplan/report/drafting.py` — `SECTIONS` is the single source of truth for section
  order, [`scripts/draft_report_sections.py`](scripts/draft_report_sections.py)):
  Investment Thesis, Bulls/Bears, Economic Moat, Valuation/Sensitivity/Scenarios,
  Financial Health (monetary-exposure grades), Market Consensus, Recommendation, Risks —
  each a separate `claude -p` call reading the JSON files above by path.
- **Stage 5 — plagiarism/references review** ([SOP](.devops/agents/equity-report/review-plagiarism-references.md),
  `bizplan/report/review.py` (imports its section list from `drafting.py` rather than
  keeping its own copy), [`scripts/review_report.py`](scripts/review_report.py)): one
  whole-document pass — cross-checks every claim, flags (doesn't silently fix)
  errors/inconsistencies, and assembles the References section.
- **Stage 6 — PDF assembly** (`bizplan/report/pdf.py`,
  [`scripts/build_report_pdf.py`](scripts/build_report_pdf.py), pure Python, no LLM):
  ReportLab + matplotlib, no system dependencies. Verified: charts render the World A/B/C
  operating-profit comparison, the per-subsidiary IAS 29 impact bars, and the 2025
  model-vs-disclosed validation gap; the monetary-exposure grade table renders correctly
  on a test document.
