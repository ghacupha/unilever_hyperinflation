# CHANGELOG

All meaningful changes to this repo. Each entry should name which `BLUEPRINT.md` phase /
`BACKLOG.md` item(s) it closes. Prior to 2026-08-09, this repo was a Family Bank Kenya
banking model — that history is preserved below rather than rewritten; the repo pivoted
to a generic REIT valuation model (first instance Acorn I-REIT) on that date.

---

## [Unreleased]

### Changed — Adapted the equity-research-report pipeline (bizplan/report/*) to the REIT domain (2026-08-11)
- Closes `BACKLOG.md` Phase 2. `bizplan/report/data.py`, `validation.py`,
  `recommendation.py`, `pdf.py`, `sourcing.py`, `pipeline.py` and `price_research.py`
  rewritten from bank field names/logic (capital/liquidity/NPL grading, book value per
  share, DDM/Residual-Income/P-B-ROE, `peer_banks`) to REIT equivalents
  (LTV/income-producing-%/payout grading, NAV per unit, NAV/DDM/Cap-Rate, `peer_reits`).
- Caught a real design bug before it shipped: a naive port of the Master Check
  validator would have required the Payout check to pass for the 3 actual years too —
  but Acorn I-REIT's own real disclosed payout ratios are genuinely below the CMA's 80%
  minimum in those years (a governance fact, not a defect), so that would have made
  `validate_model()` permanently report failure and permanently block the pipeline's
  hard validation gate. Fixed: Payout is only required to pass for projected years.
- Verified the deterministic half of the pipeline (Stages 1, 1b, 3, 6 — no `claude -p`
  involved) end-to-end against real Acorn I-REIT data, including a real generated PDF
  with a correct cover page, valuation chart, and peer-comparables table. The
  `claude -p`-driven stages (0, 2, 4, 5, 5.5) have had their SOPs and JSON field
  contracts rewritten and cross-checked against what `data.py` actually emits, but not
  yet been exercised with a live run — tracked as the next check in `BACKLOG.md`.
- Rewrote `.devops/agents/equity-report/model-sourcing.md` from scratch — it silently
  depended on `.devops/agents/bank-onboarding.md` for essential onboarding guidance, a
  file deleted in an earlier session; the SOP is now self-contained for the REIT domain.
  Updated the remaining SOPs; `section-economic-moat.md` and
  `section-valuation-scenarios.md` needed full rewrites (REIT moat sources, NAV/DDM/
  cap-rate blend methodology), others needed only field-name fixes, and
  `section-bulls-bears.md`/`section-recommendation.md`/`coherence-apply-fixes.md` needed
  no changes at all — already domain-generic.

### Changed — Pivoted repo from Family Bank Kenya banking model to a generic REIT valuation model (2026-08-09)
- Full domain rewrite: a REIT's economics (property portfolio, rental income/NOI, CMA
  regulatory limits, NAV/DDM/cap-rate valuation) share nothing with a bank's (loan book,
  IFRS 9 provisioning, deposits/NII, capital adequacy) — see `BLUEPRINT.md` Phase 1.
- Added `bizplan/financial/reit_calculations.py` and `reit_excel_renderer.py`
  (replacing `bank_calculations.py`/`bank_excel_renderer.py`, both deleted — recoverable
  via git history); rewrote `bizplan/config_loader.py`'s schema for REIT config fields.
- Added `examples/acorn_i_reit/config.py` + `research_output.md`, calibrated from Acorn
  I-REIT's own H1 2025 interim financial statements and a Kenya REITs/REOCs sector
  report — real disclosed figures, provenance-tagged, including two documented
  reconciliation gaps found in the source filing itself. Deleted
  `examples/family_bank_kenya/`.
- Verified the generated workbook's formulas with the `formulas` Python package (an
  actual Excel-formula evaluator, not just openpyxl string-writing) — this caught and
  fixed 4 real bugs before they shipped: a balance sheet that didn't balance in any
  projected year, a DDM that discounted historical actual dividends as future cash
  flows, a missing `Assumptions!` cross-sheet qualifier that made every cross-sheet
  formula silently read the wrong cell, and a property roll-forward that froze flat
  after the first projected year. Full detail in `BACKLOG.md` Phase 1.
- Renamed `scripts/build_bank_model.py` → `build_reit_model.py` (`--bank` → `--reit`,
  default instance `family_bank_kenya` → `acorn_i_reit`); updated `launch.sh`/
  `launch.bat`/`launch.ps1` to match, smoke-tested end-to-end.
- Rewrote `BLUEPRINT.md`/`BACKLOG.md` for the REIT domain; reframed `README.md`/
  `CLAUDE.md`/`AGENTS.md`. Flagged (not fixed, per `BACKLOG.md` Phase 2) that
  `bizplan/report/*` — the equity-research-report PDF pipeline — still imports the
  retired bank modules and will not currently run.

### Changed — Refocused repo onto Family Bank Kenya specifically (2026-08-09)
- Retired the generic multi-institution "onboarding" framing: deleted `agent/` (standalone
  onboarding/update agent) and `.devops/agents/bank-onboarding.md` (its SOP) — see
  `BACKLOG.md` Phase 18. Updated `AGENTS.md` and `CLAUDE.md` to drop references to them.
- Rewrote `README.md` and `CLAUDE.md` framing from "reusable bank financial model
  generator" to "Family Bank Kenya financial model"; `BLUEPRINT.md`/`BACKLOG.md` titles
  updated to match (history entries left as-is).
- Repointed `origin` at `https://github.com/ghacupha/model_family_bank.git` and pushed to
  its `main` branch.

### Added — Coherence gate (Stage 5.5) + repeatable refresh pipeline (2026-07-27)
- Fixed the root cause of two coherence bugs found in a real pipeline run: new
  `company_facts` block in `bizplan/report/data.py`'s `to_report_json()` (total
  assets/equity/deposits/net loans/book value per share, sourced only from
  `config.ACTUALS[latest actual year]` — the corrected Bank-basis figures). Updated
  `drafting.py`'s Investment Thesis SOP and `price_research.py` (+ its SOP) to require
  `company_facts` for these figures instead of `research_output.md` prose or independent
  live web research, which had let a superseded Consolidated-basis total-equity figure
  and book-value-per-share drift back into the report after this repo already fixed the
  same Bank-vs-Consolidated mixup once in `config.py`.
- Split Stage 5's (`review.py`) output into two files — `report_reviewed.md`
  (client-facing only) and a new structured `review_findings.json` — closing a real
  defect: Stage 5 had correctly diagnosed an arithmetic error in a drafted section but
  only described it in a `## Review Notes` header that Stage 6 rendered verbatim into the
  shipped PDF, uncorrected.
- New Stage 5.5, `bizplan/report/coherence.py` (`run_coherence_gate`) — an
  evaluator-optimizer loop (Stage 5 evaluates, a new targeted correction pass
  optimizes/fixes, up to 10 iterations) wired into `pipeline.py` between drafting/review
  and PDF assembly. Never re-fetches external data mid-loop; the Excel model / JSON
  ground truth always outranks report prose. `pdf.py` now renders a distinct "Unresolved
  QA Flags" appendix if the gate doesn't converge, instead of blocking forever or
  silently shipping a known-wrong report.
- New `scripts/refresh_report.py`, wiring `agent/cli.py update` (or `source_model.py`'s
  Stage 0 for an explicit re-anchor) into the full report pipeline as one repeatable,
  schedulable command — reuses all existing code, no new calculation/rendering logic.
  Closes BACKLOG.md Phase 27.

### Added — PowerShell launcher + .env-driven REPORT config (2026-07-27)
- New `scripts/launch.ps1`, a PowerShell-native counterpart to `launch.sh`/`launch.bat`
  (same venv/dependency/timestamped-output/REPORT=1 behavior; invokes the venv's
  `python.exe` directly instead of dot-sourcing `Activate.ps1`, so it isn't blocked by
  execution-policy restrictions on activation scripts).
- All three launchers now auto-load a repo-root `.env` file (existing shell-set variables
  win over `.env`'s value). New `.env.example` documents `ANTHROPIC_KEY`/`REPORT`/
  `TICKER`/`EXCHANGE`; the local (git-ignored) `.env` now sets `REPORT=1` so this machine's
  launches produce the equity-report PDF by default without passing the flag inline every
  time. `README.md` updated with the PowerShell invocation and `.env` convenience. Closes
  BACKLOG.md Phase 26.

### Added — Sources sheet + market-data citation convention (2026-07-27)
- New `config.SOURCES` (optional list of `item`/`value`/`source`/`url`/`accessed` dicts)
  and `build_sources_sheet()` in `bank_excel_renderer.py`: renders every external
  market-data input behind the Output sheet's valuation (CAPM risk-free rate/ERP/beta, all
  9 peer bank P/B ratios) as a numbered references list on a new "Sources" tab, in standard
  equity-research citation form (item cited, source hyperlinked where a URL exists, date
  accessed) — pulled from the sourcing already documented in `config.py` comments and
  `research_output.md`. Skipped entirely for an institution whose config doesn't define
  `SOURCES`. Spot-checked the underlying 2026-07-26 market research (Damodaran Kenya ERP,
  peer beta average) via live web search — genuine and current; flagged one freshness
  caveat (the risk-free rate's 2 Jul snapshot may already have moved) without silently
  overwriting a number with an unverified re-scrape. Caught and fixed a real bug during
  verification: the Damodaran citation's embedded quotes corrupted its generated
  `HYPERLINK()` formula — fixed by escaping quotes in the source label before building the
  formula string. Closes BACKLOG.md Phase 25.

### Changed — Reapplied genericity fixes on top of the merged remote history (2026-07-27)
- A prior session's uncommitted genericity fixes (`BS_SPLIT_RATIOS`, `CURRENCY_UNIT_ABBR`/
  `_units()`, `REGULATOR_NAME`, sector-concentration graceful skip) were stashed rather than
  merged before fast-forwarding 16 incoming commits, then reapplied by hand on the new base
  once the equity-report pipeline restructure landed — same fixes, renumbered to Phase 25
  since the remote had already used "Phase 23"/"Phase 24" for unrelated work. Verified
  identical rebuild output to before the refactor. Closes BACKLOG.md Phase 25.

### Changed — Restructured the equity-report pipeline into `bizplan/report/` (2026-07-27)
- Moved all generic, institution-agnostic equity-report logic into a new `bizplan/report/`
  package (`data.py`, `validation.py`, `recommendation.py`, `pdf.py` — moved as-is from
  `bizplan/financial/`; `sourcing.py`, `price_research.py`, `drafting.py`, `review.py`,
  `pipeline.py` — extracted from what had grown into substantive logic inside
  `scripts/*.py`). `scripts/*.py` are now thin CLI wrappers only (argparse + one call into
  `bizplan.report.*`), matching `scripts/build_bank_model.py`'s existing style — prompted
  directly by noticing the inconsistency between that file and the newer pipeline scripts.
- Added `bizplan/report/claude_cli.py`: a shared `run_stage()` helper replacing a `claude
  -p` subprocess-invocation block that had been copy-pasted near-identically 5 times.
- `review.py` now imports its section list from `drafting.py`'s `SECTIONS` (the pipeline's
  one source of truth for section order) instead of keeping its own hand-maintained
  duplicate — closes a real, latent risk of the two lists drifting out of sync.
- `pipeline.py`'s `generate()` now calls `sourcing`/`price_research`/`drafting`/`review`
  directly in-process instead of shelling out to run other scripts as child processes (a
  natural side effect of the logic now living in importable functions).
- Added optional `TICKER`/`EXCHANGE` fields to `config.py` (not in
  `config_loader.py`'s `REQUIRED_FIELDS` — additive, small blast radius); Stage 2 and the
  full pipeline now default to reading them from config instead of requiring
  `--ticker`/`--exchange` on every invocation. `launch.sh`/`.bat`'s `REPORT=1` mode no
  longer requires `TICKER`/`EXCHANGE` env vars as a result.
- Documented `REPORT=1` prominently in `README.md` (previously only in code comments) and
  updated its Project Structure / sheet-name tables to match current reality.
- Researched industry practice before restructuring: PyPA's src/flat-layout guidance,
  Sphinx (engine vs. per-project `conf.py`) and Cookiecutter (templating engine vs.
  generated instance) as concrete examples of drawing the generic/instance-specific
  boundary at the directory level — confirms this repo's existing `bizplan/` vs.
  `examples/<institution>/` split was already the right shape; this change extends it to
  the newer pipeline rather than introducing a new pattern.
- Purely a reorganization — no stage's behavior changed. Verified via `python -m
  py_compile` on every touched file, `--help` on every rewritten script, a fresh full
  `bizplan.report.*` import smoke test, and re-running Stage 1/validation and Stage 6 PDF
  assembly against already-known-good data to confirm identical output post-move.

### Added — Equity Research Report pipeline, Stage 6: PDF assembly + full orchestration (2026-07-26)
- `bizplan/financial/report_pdf.py`: pure Python, no LLM. Cover page, a lightweight
  markdown-to-flowables converter scoped to what the section SOPs actually produce,
  3 matplotlib charts (valuation-by-method vs. price, sensitivity, scenario
  comparison), and a peer-comparables table, via ReportLab (no system dependencies,
  so `launch.bat` keeps working unattended on Windows).
- `scripts/build_report_pdf.py` (Stage 6 CLI) and `scripts/generate_equity_report.py`
  (full Stages 1-6 orchestrator).
- `launch.sh`/`launch.bat` gained an opt-in `REPORT=1 TICKER=... EXCHANGE=...` mode;
  the default (no `REPORT`) path is unchanged and re-verified working.
- Added `reportlab` and `matplotlib` to `scripts/requirements.txt`.
- **Live-tested twice**: an isolated Stage 6 run produced a valid 11-page PDF (verified
  via `pypdf`) from the earlier Stage 1-5 test output. Then a fully unattended full-
  pipeline run hit the Claude subscription's session usage limit partway through Stage
  5 — Stage 5 had already written a complete, valid `report_reviewed.md` before the
  process exited non-zero, so recovery was just re-running Stage 6 against the
  already-good file. Final deliverables (workbook + PDF) landed correctly together in
  `output/<timestamp>/`. See BLUEPRINT.md for the full finding, including the
  idempotent-by-file-existence lesson for production hardening.

### Added — Equity Research Report pipeline, Stage 5: plagiarism/references review (2026-07-26)
- `.devops/agents/equity-report/review-plagiarism-references.md`: SOP for the one
  whole-document pass over all 8 Stage 4 sections — cross-checks claims against source,
  flags near-verbatim copying and cross-section contradictions, assembles a
  deduplicated References list, appends the standard Disclaimer.
- `scripts/review_report.py`: orchestrator, same subscription-billed `claude -p`
  convention as earlier stages.
- **Live-tested against the real Stage 4 output and genuinely earned its keep**: caught
  2 real arithmetic errors introduced during independent section drafting, 1 real
  cross-section inconsistency (two sections quoting different liquidity figures — one
  had mixed in an actual-year disclosed ratio where a projected value belonged), and 1
  genuine unresolved cross-file discrepancy (Stage 2's live-researched peer P/B vs. the
  figures already in `config.py`). All flagged under a `## Review Notes` header, not
  silently rewritten, per the SOP's explicit instruction.

### Added — Equity Research Report pipeline, Stage 4: per-section report drafting (2026-07-26)
- 8 section SOPs under `.devops/agents/equity-report/section-*.md` (Investment Thesis,
  Bulls/Bears, Economic Moat, Valuation/Sensitivity/Scenarios, Financial Health, Market
  Consensus, Recommendation, Risks & Uncertainty — consolidated from the original
  ~13-section proposal; Cover/Peer-table/Disclaimer need no LLM and are left to Stage 6).
- `scripts/draft_report_sections.py`: orchestrator, one `claude -p` call per section,
  same subscription-billed convention as Stages 0/2.
- `bizplan/financial/report_data.py`: added `financial_health_grade()` (pure Python,
  documented threshold rule) and wired it into `to_report_json()`'s output.
- **Live-tested, full 8-section batch**: uniformly high quality, every number traced to
  the JSON inputs, no fabrication detected, genuine Bulls/Bears tension, honest "None"
  moat rating.
- **Important finding**: the Recommendation section, tested twice independently on
  identical data, reached different conclusions (Sell vs. Hold) — both well-reasoned,
  genuine run-to-run variability in LLM catalyst judgment on a borderline call, not a
  bug. Documented in BLUEPRINT.md as an open characteristic to account for, not resolved.

### Added — Equity Research Report pipeline, Stage 3: mechanical Buy/Hold/Sell (2026-07-26)
- `bizplan/financial/report_recommendation.py`: pure Python, no LLM. Applies
  Morningstar's real published margin-of-safety bands (Low 20%/25% ... Extreme
  75%/300%) to price vs. this model's blended fair value, using the DDM/RI/P-B-ROE
  method-spread (coefficient of range) to pick an Uncertainty tier — this repo's own
  heuristic mapping, documented as such, not a literal Morningstar practice.
- Tested against real Stage 1+2 output: Family Bank Kenya's 3 methods disagree by 217%
  → "Extreme" tier → the market's +94.8% premium to blended fair value (27.65 vs.
  14.20/share) still falls inside the wide Extreme band → mechanical signal `Hold`,
  correctly deferring to a report-writing stage to argue a specific catalyst rather
  than forcing Sell off raw dispersion. Also sanity-checked a tight-agreement ("Low"
  uncertainty) case, which correctly triggers `Buy` at a much narrower 20% threshold.

### Added — Equity Research Report pipeline, Stage 2: price/consensus research (2026-07-26)
- `.devops/agents/equity-report/price-consensus-research.md`: SOP for researching
  share price and analyst consensus (or a documented proxy when none exists), with
  explicit reference-date handling so a backtest run can't leak hindsight.
- `scripts/research_price_consensus.py`: orchestrator, same `claude -p`
  subscription-billed convention as Stage 0.
- **Live-tested**: found Family Bank Kenya's real share price (KES 27.65, 24 Jul 2026)
  and correctly determined no analyst consensus exists yet (recently listed), falling
  back to a documented peer-average-P/B proxy (KES 18.25) exactly as the SOP specifies.

### Added — Equity Research Report pipeline, Stage 0: model sourcing (2026-07-26)
- `.devops/agents/equity-report/model-sourcing.md`: SOP generalizing
  `bank-onboarding.md` along a second axis — institution *and* an as-of anchor year
  (actuals = the 3 years ending there, projections = the next 5), supporting both
  roll-forward (seasonal updates) and roll-backward (backtesting) re-sourcing.
- `scripts/source_model.py`: orchestrator invoking `claude -p` (Claude Code's headless
  mode, subscription-billed) instead of the raw-API-billed `agent/` module, then
  deterministically validating (`bank_validation`) and rebuilding the workbook.
- **Live-tested end-to-end**: ran against `family_bank_kenya --as-of 2025` for real —
  correctly recognized the anchor already matched, left `config.py` untouched, only
  annotated `research_output.md`. Validation and rebuild both passed.

### Added — Equity Research Report pipeline, Phase A: ground-truth JSON + validation (2026-07-26)
- `bizplan/financial/bank_validation.py`: `validate_model()` re-implements the Model
  sheet's Excel "Master Check" (Balance Sheet, Capital Adequacy, Liquidity) as a pure
  Python function, same tolerances, so a pipeline can gate on model integrity without a
  spreadsheet engine. Tested against Family Bank Kenya: all 3 checks pass for every
  projected year.
- `bizplan/financial/report_data.py`: `compute()`/`to_report_json()` serialize
  `build_all()`/`build_scenarios()`/`build_sensitivity()` into the JSON shape a later
  equity-research-report pipeline's writing stages will read — the intended
  anti-hallucination boundary (every number an LLM narrates should trace back to this
  file, not a paraphrase). First phase of a larger preliminary architecture — see
  BLUEPRINT.md's "Equity Research Report pipeline" section and BACKLOG.md's Phase 24.

### Added — Blended valuation, per-scenario valuation table, Net Income sensitivity (2026-07-26)
- New "Blended Valuation" section on the Output sheet: a weighted combination of DDM,
  Residual Income, and P/B-ROE regression (50/30/20 default, configurable on the
  Assumptions sheet), live-formula-linked like the rest of the Base Case. Weighting choice
  is grounded in a review of how equity-research analysts and Damodaran actually combine
  these methods for banks — see BLUEPRINT.md's "2026-07-26" section for the full research
  and citations.
- New "Implied Value Per Share by Scenario" table on the Summary sheet (Base/Best/Worst ×
  DDM/Residual Income/P-B-ROE/Blended) — Best/Worst valuation was already computed by
  `build_scenarios()` but never rendered anywhere until now.
- New "Key Net Income Sensitivities" section on the Summary sheet, from a new
  `bank_calculations.build_sensitivity()` that shocks one driver at a time (vs. the
  existing Best/Worst scenarios, which move several levers together). Three factors cross
  a >10% average-PAT threshold: loan/balance-sheet growth, asset yield (lending rate), and
  cost of funds (deposit pricing) — loss rate and opex escalation were tested and don't
  cross 10% at their currently configured scenario magnitudes.

### Changed — Resolved remaining `[PLACEHOLDER]` valuation assumptions (2026-07-26)
- Equity risk premium: 9.5% generic placeholder → 13.94% (Damodaran's total Kenya ERP,
  Jan 2026 data update).
- Beta: 1.0 neutral midpoint → 0.55 (average of 6 NSE-listed Kenyan peer banks' published
  equity betas; Family Bank itself is too newly listed, 23 Jun 2026, for its own beta).
- Peer bank P/B ratios: the remaining 7 of 9 peers (Absa, Co-op Bank, DTB, Equity Group,
  KCB Group, Stanbic Holdings, StanChart) now use current NSE price / book value per share
  instead of illustrative placeholders.
- Net CAPM effect: cost of equity moves from 21.82% to ~19.99% — the higher Kenya-specific
  ERP and lower measured peer beta largely offset. Residual Income turns positive in Year 1
  (was negative in every year under the placeholder inputs) though still negative in Years
  2-5 as projected ROE keeps declining below the (still high) cost of equity.
- All figures sourced via live web search/fetch, documented with source + accessed date in
  `research_output.md`'s 2026-07-26 entry. Closes BACKLOG.md's "Damodaran ERP", "beta",
  and "peer market cap/book equity" follow-up items.

### Fixed — Scenarios-sheet CHOOSE formula off-by-one (2026-07-14)
- `_scenario_metric_block()` double-incremented the row cursor right after the ACTIVE row,
  shifting Base/Best/Worst one row below where the `CHOOSE()` formula's operands actually
  pointed — Base always evaluated to 0 (reading a blank cell), and Best/Worst each picked
  up the wrong case's data. Fixed by removing the extra increment and relocating the blank
  spacer to between the title bar and the ACTIVE row instead. Verified across all 8
  Scenarios-sheet metric blocks with zero mismatches. Closes BACKLOG.md Phase 19.

### Changed — Visual/layout refinements + Assumptions tables (2026-07-14)
- The boxed live/ACTIVE row now uses a single outlined-group border (`outline_range()` in
  `xl_helpers.py`) instead of bordering every cell individually; data columns narrowed
  (14→12 globally, H-J collapsed to width 3 on the Scenarios sheet where they're unused) to
  close the dead space the boxed rows sat in. Closes BACKLOG.md Phase 20.
- Assumptions sheet's Loan Book and Deposits sections restructured from repeated per-
  category vertical blocks into tables (one header row naming each category, one row per
  metric spanning all categories) — Loan Book goes from 36 rows to 12, Deposits from ~12 to
  3. Required extending `_assum_ref()` to resolve a `(row, col)` tuple in addition to the
  existing bare-row-int form, so per-category assumptions can live in their own column
  without any changes to the ~15-18 Model-sheet call sites that read them. Closes
  BACKLOG.md Phase 21.

### Added — `.env` for the agent (2026-07-14)
- `.env` (git-ignored) with `ANTHROPIC_KEY=`; `agent/cli.py` now loads it explicitly via
  `python-dotenv` rather than relying on the Anthropic SDK's default
  `ANTHROPIC_API_KEY`/`ANTHROPIC_AUTH_TOKEN` auto-detection, since this repo uses its own
  variable name. Closes BACKLOG.md Phase 22.

### Added — Standalone onboarding/update agent (2026-07-14)
- New `agent/` package: a standalone Python program (calls the Anthropic API directly,
  not a Claude Code subagent) that researches a new institution's public filings via a
  web-search + PDF-download tool-use loop, extracts the modelling facts, writes
  `examples/<institution>/config.py` + `research_output.md`, and runs the existing
  renderer unchanged. `agent update <institution>` re-checks for newer filings and rolls
  the config forward. SOP at `.devops/agents/bank-onboarding.md`; index at `AGENTS.md`.
  Closes BACKLOG.md Phase 18.

### Changed — Scenario metric block redesign, printer-friendly output (2026-07-14)
- Assumptions and Scenarios sheets reworked to a compact table convention: a title bar
  carrying the metric name/unit once, a boxed live `CHOOSE()`-driven row on top, then
  plain Base/Best/Worst rows below (short labels only) — replacing the old repeated
  4-row-per-item layout and the Scenarios sheet's case-grouped blocks. Closes BACKLOG.md
  Phase 16.
- Added landscape/scaled/print-area page setup to every sheet (multi-block on Model, one
  per schedule section) and a top-right, per-page `HYPERLINK()` scenario banner that
  repeats on every printed page via `print_title_rows`. Closes BACKLOG.md Phase 13-14.
- Added a native Data Validation dropdown (1/2/3) to the `Scenarios!D5` switch cell.
  Closes BACKLOG.md Phase 17.
- Renamed the "Valuation" sheet to "Output" throughout the renderer and `BLUEPRINT.md`
  for reusability across future institutions. Closes BACKLOG.md Phase 15.

### Removed — Root-level duplicate files (2026-07-14)
- Deleted `bank_calculations.py`, `bank_excel_renderer.py`, `xl_helpers.py`,
  `config_loader.py`, `config.py`, `build_bank_model.py`, `__init__.py`, the root
  `financial/` directory, and root `launch.bat`/`launch.sh` — confirmed byte-identical
  duplicates of `bizplan/`/`scripts/` files never touched by the live launch path. Closes
  BACKLOG.md Phase 12.

### Added — Per-share equity valuation (2026-07-06)
- New `SHARES_OUTSTANDING_2025` (1,662.655m shares, `[DISCLOSED]` — FY2025 report's share
  capital note, KES 1.00 par value confirmed). Added "Implied Value Per Share (KES)"
  under each of the DDM/Residual Income/P-B-ROE Regression models, and a Per Share column
  in the Summary comparison table, alongside the existing aggregate KES MM figures.
- New "Book Value Per Share (Actuals)" cross-check row (2023-2025), each year using its
  own share count (share count changed via the FY2023 rights issue and FY2025 private
  placement) — verified against Family Bank's own disclosed BVPS trend (17.15→19.62,
  Consolidated basis); our Bank-basis figures come in slightly lower, as expected.

### Fixed — CAPM formula missing leading `=` (2026-07-06)
- The Valuation sheet's Risk-free rate/Beta/ERP/Cost of equity cells were missing the
  leading `=` on their cross-sheet reference formulas, so Excel stored them as literal
  text instead of live formulas — cascaded into a `#VALUE!` error on Terminal Value and
  the Residual Income model. Fixed all 4 cells.

### Fixed — Bank (standalone) vs Consolidated (Group) data correction (2026-07-06)
- Every actual figure in `config.py` had been sourced from Family Bank's **Consolidated
  (Group)** column, not the **Bank (standalone)** column both are disclosed in — caught
  while rebuilding the Balance Sheet's line-item detail. Per the principle that a bank in
  a group should be modeled on its own bank data, re-sourced every Balance Sheet, Income
  Statement, and Cash Flow actual figure to the Bank column for 2023-2025 (see
  `research_output.md` for the full reconciliation, including two real "cash and cash
  equivalents" definition restatements found along the way). Cascading corrections to
  `DEPOSIT_TYPES`, `INVESTMENT_SECURITIES`, `PPE`, `CAPITAL['opening_tier1']`,
  `OPEX_ITEMS`, `NON_INTEREST_INCOME_RATE` — all numerically derived from the FY2025 Bank
  figures. `bank_calculations.py` needed no code changes.

### Added — Full Balance Sheet line-item detail + scroll-safe headers (2026-07-06)
- The Model sheet's Balance Sheet block went from a single "TOTAL ASSETS" row and 3
  liability/equity aggregates to all ~28 real disclosed line items, matching Family
  Bank's own statement structure. Actual years hardcode the real Bank-basis facts;
  projected years reuse whichever driver already exists (Cash Flow roll-forward,
  securities growth, the Loan Book schedule, PP&E roll-forward — split into
  presentational sub-lines via the FY2025 mix) or grow independently at a new generic
  `OTHER_BS_ITEMS_GROWTH_RATE` where nothing is disclosed. Retained Earnings becomes a
  residual/plug for projected years that preserves the pre-existing Total Equity
  roll-forward exactly (proven algebraically, not just numerically) — the Balance Sheet
  Check's tie-out was never at risk.
- New `_linked_year_header_row()`: every Model-sheet schedule now repeats a
  formula-linked copy of the sheet's single master year-header row, so scrolling the
  ~250-row sheet never loses the column-to-period mapping. Columns relabeled
  "2023A"/"2026P"-style across every sheet with year columns (Model, Summary, Scenarios,
  Valuation).

### Verified
- All 3 actual years' granular Balance Sheet rows sum to the real disclosed Total
  Assets/Liabilities/Equity exactly. Balance Sheet Check ties for all 8 years and all 3
  scenarios (Base/Best/Worst) — `bank_calculations.py`'s Python ground truth is
  unaffected by the renderer rework. Hand-traced the full Excel formula chain for
  2023-2025 and the first projected year. Header-linking formulas and period-suffix
  labels confirmed across all 4 sheets.

### Added — CLI wiring, regulatory capital bridge, sector concentration (2026-07-06)
- `scripts/build_bank_model.py` now takes `--bank NAME` (default `family_bank_kenya`) or
  `--config PATH`, so the generator can target a different bank instance without editing
  code; both launchers accept an optional positional bank-name arg and pass it through.
  `bizplan/config_loader.py`'s `REQUIRED_FIELDS` now includes `ACTUALS`, `ACTUAL_YEARS`,
  `REGULATORY_CAPITAL` (a validation gap from the previous session — the renderer already
  required the first two).
- **Regulatory capital bridge**: found that `CAPITAL['opening_tier1']` was total
  accounting equity (32,622.486), not real regulatory Tier 1 capital (24,404.354 for
  FY2025, per Family Bank's own Capital Management note) — the exact reason the modeled
  Core/Total Capital ratios didn't reconcile to the disclosed 16.9%/19.6%. Added
  `config.py`'s `REGULATORY_CAPITAL` (real Tier 1/Tier 2/RWA build-up, 2023-2025) and
  reworked the Model sheet's Capital Adequacy section to show the real build-up (Share
  Capital/Premium/Retained Earnings/Less Deferred Tax → Tier 1; Revaluation/Subordinated
  Debt/Statutory Reserve → Tier 2) for actual years, with real disclosed RWA (Family
  Bank's own filings don't disclose a Basel credit/market/operational RWA split, so there
  was nothing finer to model). Projected years now use `tier1_pct_of_equity`,
  `reg_tier2_opening`, and `other_rwa_pct_of_gross_loans` — new drivers calibrated to the
  real FY2025 anchor point, replacing the old disconnected accounting-equity proxy and
  flat RWA plug. The accounting Balance Sheet mechanics are untouched — regulatory capital
  is a genuinely parallel calculation (real Tier 2 includes statutory/revaluation reserve,
  which sit within accounting equity, not liabilities).
- **Sector concentration**: no CBK single-borrower/large-exposure limit or Family Bank's
  actual largest exposures are disclosed anywhere (confirmed via targeted search of 4
  annual reports) — skipped rather than fabricate a check with nothing real to verify
  against. Added a "Loan Book Concentration — Sector Detail" schedule instead, using the
  real disclosed sector-by-loan tables (FY2024/FY2025 in a 10-category scheme, FY2023
  separately in the prior 7-category scheme Family Bank used before restating).

### Verified
- Actual-year Core Capital/RWA and Total Capital/RWA tie exactly to Family Bank's
  disclosed 13.47%/18.89% (2023), 13.52%/17.76% (2024, restated), 16.87%/19.56% (2025).
  Balance Sheet Check still ties for all 8 years across Base/Best/Worst (unaffected by
  the regulatory capital changes). Projected-year CAR continues smoothly from the FY2025
  anchor. Sector concentration table totals match disclosed totals exactly. CLI flags
  (`--bank`, `--config`, invalid-bank error path) and both launchers tested directly.

### Added — Historical actuals (2023-2025) + Financial Statement Quality Analysis (2026-07-06)
- Every Model-sheet schedule (Loan Book/IFRS 9, Securities/Deposits/Interest/NII, Income
  Statement, Cash Flow/Balance Sheet, Capital Adequacy/Liquidity) now shows 3 real actual
  years (2023-2025, hardcoded disclosed facts) immediately followed by the 5 projected
  years (2026-2030, live formulas) — matching Blu Containers' own H,I,J | K,L,M,N,O column
  pattern instead of just anchoring 2026 to real data. `_prev()` simplified: the first
  projected period now references the last actual column directly on the same sheet, no
  Assumptions-cell fallback needed. Ratio Disclosures (Summary sheet) and the Master Check
  extended to span all 8 years; Scenarios sheet stays projected-only (actuals aren't
  scenario-dependent).
- `config.py`: new `ACTUALS` dict (per-year real disclosed loan/ECL/balance sheet/income
  statement/cash flow figures for 2023/2024/2025, extracted from Family Bank's annual
  reports) and `ACTUAL_YEARS`. All 3 years reconcile exactly (Assets − Liabilities −
  Equity = 0).
- New "Financial Statement Quality Analysis (Actuals only)" section on the Valuation
  sheet: Sloan (1996) Accruals Ratio, PAT-vs-OCF divergence trend with a decline flag, the
  Texas Ratio (bank-specific distress indicator), and an adapted Beneish M-Score proxy
  (bank-equivalent substitutions per component, DEPI omitted, prominent caveat that the
  standard model excludes financial institutions and its -2.22 threshold doesn't apply
  here) — scoped to the 3 actual years only, since the projection is our own modeling, not
  a filing to scrutinize.

### Fixed
- Actual-year Total Assets was built from the Cash Flow Statement's own "cash and cash
  equivalents" figure, which is narrower than the Balance Sheet's "cash and balances with
  CBK + due from banks" — caught via hand-trace verification (Balance Sheet Check was off
  by exactly the inter-bank-balances amount each year). Fixed by using the correct
  Balance-Sheet-definition cash figure for the Total Assets build-up on actual columns;
  check now ties to 0.0 for all 3 actual years.

### Verified
- Balance Sheet Check ties for all 3 actual years and all 5 projected years across
  Base/Best/Worst (recomputed directly via `bank_calculations.py`). Hand-traced the Texas
  Ratio and the 2024 Beneish M-Score proxy against independent Python ground truth (exact
  match).

### Added — Timestamped output folder convention (2026-07-06)
- `scripts/launch.sh` / `scripts/launch.bat` now create `output/<YYYY-MM-DD_HHMMSS>/` per
  run, export it as `OUTPUT_DIR`, and copy `config.py` into it after the build — matching
  `colossal-visuals`' convention exactly (checked directly against its `launch.sh`).
  `scripts/build_bank_model.py` reads `OUTPUT_DIR`, falling back to writing straight into
  `examples/family_bank_kenya/` when run without a launcher.
- Removed stale pre-convention artifacts (`examples/family_bank_kenya/
  Family_Bank_Kenya_Financial_Model.xlsx`, its Excel lock file, `__pycache__/`).
- Verified: repeated launcher runs create fresh timestamped folders (not overwriting);
  `output/` already covered by the root `.gitignore`; standalone (no-launcher) run still
  falls back correctly.


### Added — Structural review + CHOOSE-switch scenario architecture (2026-07-06)
- Compared the generated workbook against the actual FMI reference file cell-by-cell
  (fills, fonts, formulas) rather than relying on documented conventions. Confirmed our
  font-color tiers are exactly right; found the reference uses zero colored fills (kept
  ours anyway, by choice) and a single scenario-switch cell that makes the whole Model
  sheet reactive to Base/Best/Worst (we didn't have this — built it).
- `bizplan/financial/bank_excel_renderer.py`: `SWITCH_CELL_REF` (`'Scenarios'!$D$5`) and
  `_scenario_row()` — every scenario-dependent assumption (loan growth, IFRS 9 loss rates,
  deposit growth, opex escalation) now renders as Base/Best/Worst/ACTIVE rows, with Model
  -sheet formulas following the ACTIVE (CHOOSE-driven) row automatically. Added the
  "CURRENTLY RUNNING: X SCENARIO" banner (Model sheet, row 1), matching the reference.
- `examples/family_bank_kenya/config.py`: `SCENARIO_MULTIPLIERS` — single source for both
  `bank_calculations.build_scenarios()` and the renderer's CHOOSE-switch formulas.

### Changed — Re-anchored to FY2025, real peer data
- `data/` reorganized into per-bank subfolders (`family_bank/`, `absa/`, `co-op/`, `dtb/`,
  `equity/`, `i&m/`, `kcb/`, `ncba/`, `scb/`, `stanbic/`) with re-downloaded annual reports;
  the 4 previously-broken Family Bank PDFs are fixed.
- `config.py`: `YEARS` moved to `[2026, 2027, 2028, 2029, 2030]`; opening balance sheet
  moved from FY2023 to FY2025 actual (full real balance sheet, income statement, and IFRS 9
  stage table extracted — see `research_output.md`'s "Update 2026-07-06" section).
  `PEER_BANKS` updated with real disclosed/derived P/B for NCBA (1.2x) and I&M (~0.64x).
- Verified: balance sheet ties for Base/Best/Worst on the new basis; hand-traced a Model
  -sheet formula against Python ground truth (exact match).


### Added
- `scripts/launch.sh` (Unix/macOS/Linux) and `scripts/launch.bat` (Windows) — the intended
  entry point going forward. Each creates `.venv` at the repo root if it doesn't exist,
  activates it, installs `scripts/requirements.txt`, then runs `build_bank_model.py`. No
  PowerShell variant, per instruction. `scripts/requirements.txt` added (`openpyxl>=3.1.0`
  — the only runtime dependency the build itself needs).

### Changed
- `BLUEPRINT.md` no longer references `colossal-visuals/` anywhere — it's confirmed as a
  standalone example due for removal, so the design doc is now fully self-contained
  (inlined what used to be pointers to its `CLAUDE.md`/`xl_helpers.py`). Replaced the old
  "Repo layout" section with a full "Project structure" section covering the launchers.

### Added
- `bizplan/financial/bank_excel_renderer.py` — full workbook renderer: Cover, Summary,
  Assumptions (four-color provenance legend, ~103 tracked assumption cells, P/B-ROE
  regression via native Excel `SLOPE()`/`INTERCEPT()`), Scenarios (Best/Worst static),
  Model (Master Check, Loan Book/IFRS 9, Securities/Deposits/Interest/NII, Income
  Statement, Cash Flow/Balance Sheet, Capital Adequacy/Liquidity — all live formulas),
  Valuation (DDM/Residual Income/P-B regression). Closes Phase 3.
- `bank_calculations.build_scenario()`/`build_scenarios()` — Best/Worst scenario flexing
  for the Scenarios sheet (Python-computed static values, per the established convention).

### Fixed
- Renderer's Other-Liabilities opening-plug formula used gross loans instead of net loans
  (caught during formula verification — cross-checking OCF year 1 against
  `bank_calculations.py`'s ground truth off by exactly the ECL amount). Fixed; OCF now
  matches exactly for year 1 and year 2, and total assets/RWA match exactly for year 1.

### Verified
- `scripts/build_bank_model.py` runs end to end. Sheet tab order correct. Model sheet:
  455 live formulas, 0 bare numeric values in data columns. Assumptions sheet: 107 inputs
  + 4 derived formulas. Known gap: no LibreOffice on this machine to auto-recalculate and
  confirm the Master Check literally shows "OK" — needs manual confirmation in Excel.


### Changed
- Moved all bank-model code out of `colossal-visuals/` to the repo root:
  `bizplan/financial/{xl_helpers,bank_calculations}.py` and
  `examples/family_bank_kenya/{config.py,research_output.md}`. `colossal-visuals/` has its
  own nested `.git` and is a standalone reference example, not part of this repo's real
  deliverable — confirmed untouched. Uninstalled the stale colossal-visuals editable
  `bizplan` registration from the shared `.venv`. Added `bizplan/config_loader.py` and
  `scripts/build_bank_model.py` (entry point, no packaging ceremony — plain
  `sys.path.insert`). Re-verified after the move: identical output to before relocation.

### Added
- `BLUEPRINT.md` — design source of truth for the reusable bank financial model generator
  (Family Bank Kenya as first instance): schedule design, IFRS 9 provisioning design,
  valuation approach, analytical framework. Closes Phase -1.
- `BACKLOG.md` — phase-by-phase task tracking against the blueprint. Closes Phase -1.
- `CHANGELOG.md` — this file. Closes Phase -1.

### Added
- `colossal-visuals/examples/family_bank_kenya/config.py` — first-pass Family Bank Kenya
  config. Year 0 (opening balance sheet) is FY2023, the most complete real disclosure
  available; forecast years 2024-2028 deliberately overlap real subsequent actuals so
  Year 2 (2025) can be spot-checked against the real disclosed FY2025 aggregates. Every
  assumption tagged inline as `[DISCLOSED]`, `[DISCLOSED-DERIVED]`, `[MODELED]`, `[MACRO]`,
  or `[PLACEHOLDER]`. Closes most of Phase 4's config item (research_output.md already
  covered the research half).
- `colossal-visuals/bizplan/financial/bank_calculations.py` — all 16 schedules from
  BLUEPRINT.md (loan staging, IFRS 9 ECL, securities, deposits, interest income/expense,
  NII, non-interest income, opex, income statement, cash flow, balance sheet, capital
  adequacy, liquidity, ratio disclosures, valuation). Closes Phase 2.

### Fixed
- Balance-sheet check initially failed with a constant KES 8,828.1m discrepancy across all
  5 forecast years (not growing — a signal it was an opening-balance issue, not a
  roll-forward bug, confirmed algebraically). Root cause: opening Other Liabilities was
  computed as a ratio of deposits rather than a plug, so the modeled Year-0 balance sheet
  didn't tie by construction. Fixed by making opening Other Liabilities the balancing plug;
  forecast years still use the ratio mechanic. Balance sheet now ties exactly
  (check = 0.0 all 5 years). This is exactly the kind of error the Master Check section
  (Phase 3) exists to catch in the rendered workbook, so worth having caught it here first.

- `colossal-visuals/bizplan/financial/xl_helpers.py` — formula-capable rendering
  primitives ported from `scripts/xl_helpers.py`, self-contained within the `bizplan`
  package. Smoke-tested (formula strings render correctly, e.g. `=IF(H5<>0,H2/H5,0)`).
  Adds `ORANGE` as the fourth data-provenance colour (disclosed input / formula /
  cross-sheet ref / modeled proxy). Closes Phase 1.

### Decided
- **Modeleon spike (Phase 0): decided against Modeleon, building on `xl_helpers.py`
  instead.** Confirmed Modeleon genuinely emits live Excel formulas with working
  recurrence and cross-sheet references, but its Excel writer only wires `number_format`
  through to cells (`modeleon/compile/excel/writer.py:253-259`) — `bold`/`bg`/`font_color`
  passed to `set_style()` are silently dropped — and its layout engine is rigid (one row
  per Variable, fixed label/data columns), incompatible with the FMI vertical convention's
  spacer/units columns, indentation, and section-header bars. Closes Phase 0.
- `pypdf` and `pdfplumber` installed into the repo-root `.venv`. Closes part of Phase -0.5.

- `colossal-visuals/examples/family_bank_kenya/research_output.md` — calibration figures
  extracted from `data/`: real IFRS 9 stage-level loan/ECL tables (2022-2023), CBK capital
  and liquidity minimums confirmed from Family Bank's own disclosures, FY2023 actuals, a
  9-bank peer comparables table (EPS/ROAE/payout/DPS), and forward-looking Kenya banking
  sector outlook (NIM, NPL, RBCPM rollout). Partial progress on Phase -0.5 / Phase 4.

### Data quality finding
- 4 of 8 files in `data/` are broken and need re-downloading: `-2024.pdf` is truncated on
  disk (589KB of a declared 27.2MB); `-2025.pdf`, `-2021-1.pdf`, and the (older) MTN
  memorandum have correct byte counts but a Catalog missing `/Pages` even after `pikepdf`
  recovery; `-2022.pdf` fails recovery entirely. The 2023 annual report and the newer MTN
  memorandum (`ke-fmly-2026-ps-00.pdf`, covers FY2021-2025) are fully usable and were the
  source for the research output above. Full detail in `research_output.md`.

### Planning notes
- Confirmed `modeleon` is a real early-stage PyPI package (v0.1.3); plan is to spike it
  before committing (Phase 0).
- Confirmed repo-root `.venv` (Python 3.13.2) is ready; `pypdf`/`pdfplumber`/`modeleon`
  reachable on PyPI but not yet installed.
- Located `data/` (repo root): five years of Family Bank Kenya annual reports (2021-2025),
  MTN Information Memorandum, IPO/listing prospectus documents — primary calibration source
  for the model, superseding secondary web-search figures.
