# CHANGELOG

All meaningful changes to this repo. Each entry should name which `BLUEPRINT.md` phase /
`BACKLOG.md` item(s) it closes. Prior to 2026-08-09, this repo was a Family Bank Kenya
banking model; it pivoted to a generic REIT valuation model (first instance Acorn I-REIT)
on that date, then pivoted again on 2026-09-27 to a CFA Level II hyperinflation-accounting
teaching model (Unilever plc) — both prior domains' history is preserved below rather
than rewritten.

---

## [Unreleased]

### Changed — Refreshed the checked-in sample with a second full live run (2026-09-27)
- A second `REPORT=1 ./scripts/launch.sh unilever` run, now that `config.py` carries the
  peer-comparison and standard-setting content added earlier the same day — confirmed
  live (not assumed) that Stage 4's drafted sections correctly pull in the new
  Colgate/Reckitt/BBVA/IFRS-IC material. The coherence gate used its full 10-iteration
  budget this time (still converging to 0 unresolved findings on the last one, not a
  QA-flags ship) — genuinely more to catch with more cited material in play, including a
  moat-rating headline contradicting its own per-market verdict and a Recommendation
  section briefly contradicting its own Hold call.
- Deleted the old `examples/2026-09-27_142024/` sample, replaced it with
  `examples/2026-09-27_222102/`, regenerated `docs/screenshots/*.png` from the new PDF,
  and updated every current-state doc pointer (`README.md`, `AGENTS.md`,
  `research_output.md`, `config.py`, `BACKLOG.md`) to the new path. This entry's own
  sibling below ("First live run...") describing the old path is left untouched — it's
  an accurate historical record of what happened then, not a live pointer.

### Added — Two more real peers: a US GAAP/IFRS natural experiment (2026-09-27)
- Extends `BACKLOG.md` Phase 7. Added Colgate-Palmolive and Reckitt Benckiser to
  `PEER_COMPARISON` after checking whether a true household-goods peer existed (Coca-Cola
  FEMSA is a bottler; BBVA a bank). Fetched and read the actual 10-K/annual-report PDFs
  directly rather than relying on search snippets — search alone didn't surface either
  finding. Colgate (US GAAP) names Argentina/Türkiye/Nigeria "highly inflationary" and
  discloses no dollar impact, stating it's immaterial — a real-world instance of this
  model's own "Flag: immaterial" conclusion for Unilever, reached independently under the
  temporal method (this model's World B, in actual production use). Reckitt (IFRS, same
  IAS 29 regime as Unilever) bundles hyperinflation into one undifferentiated "Exchange
  and hyperinflation" reconciling item rather than a separate net-monetary line, and
  fully divested its Argentina business on 31 Dec 2025 as part of a £2.2bn segment sale.
  Framed honestly in `research_output.md` as a disclosure-granularity contrast, not a
  clean number-matching table, since neither peer's figure is directly comparable to
  Unilever's or BBVA's.

### Added — Portfolio polish: README, CI, interactive demo (2026-09-27)
- Closes `BACKLOG.md` Phase 9. Added a "What this demonstrates" section to `README.md`
  (technical accounting depth, verified formula-linked Excel engineering, the real
  coherence-gate catches, 51 tests in CI, git-history hygiene), plus two screenshots
  (`docs/screenshots/`, rendered from the checked-in sample PDF via PyMuPDF and cropped
  to content) embedded near the top.
- Added `.github/workflows/tests.yml` — runs the full test suite (including the
  calibration-fidelity regression test) plus an Excel-model build smoke test, on every
  push/PR to `main`.
- Added `scripts/build_interactive_demo.py`, generating a self-contained
  `docs/demo/index.html` (no external scripts/server, works via `file://`) with the
  real model's World A/B/C data embedded inline and toggle buttons that update the
  displayed figures — a plain repo file rather than a Claude Artifact, so it travels
  with the repo. Verified by hand (brace/script-tag balance checks, a full line-by-line
  JS read, every `DATA` field access cross-checked against the generator's output) since
  no browser tooling was available this session to render it directly.

### Added — Peer-comparison and standard-setting content (2026-09-27)
- Closes `BACKLOG.md` Phase 7. Added `PEER_COMPARISON` (Coca-Cola FEMSA's Argentina
  net-monetary-position gain; BBVA's real disclosed Türkiye net-monetary-loss and
  inflation-linked-bond-offset figures, FY2022/FY2023) and `STANDARD_SETTING_NOTE` (the
  IFRS Interpretations Committee's July 2025 agenda decision on qualitative
  hyperinflation indicators) to `examples/unilever/config.py`, surfaced through
  `data.to_report_json()` as optional fields, written up with full citations in
  `research_output.md`, and referenced in the `section-valuation-scenarios.md` and
  `section-risks-uncertainty.md` SOPs. 4 new tests.
- Also fixed two stale fields found while in there: `CONSENSUS` and `VALUATION` in
  `config.py` were still marked `[PLACEHOLDER]` after the live pipeline run had already
  confirmed the market-perception hypothesis (see the "First live run" entry below) —
  updated both to state the confirmed finding; `VALUATION`'s note also still described
  the old pre-rewrite NAV/DDM/cap-rate design instead of the current materiality-flag one.

### Added — BDD feature specs (2026-09-27)
- Closes `BACKLOG.md` Phase 8 fully. 3 `pytest-bdd` feature files under
  `tests/features/` (15 scenarios): `calibration.feature` (a Scenario Outline covering
  both subsidiaries × all 4 disclosed impact metrics, plus a deliberately-broken-
  calibration scenario), `recommendation.feature` (the materiality-threshold decision
  logic plus the real Unilever case), and `report_data_generation.feature` (the
  deterministic-stages-only output-generation behavior — scenario comparison and
  monetary-exposure grades in the generated report JSON, and consistency between that
  JSON and the mechanical recommendation reading it). Chose `pytest-bdd` over `behave`
  so both suites share one runner/one CI hook. Shared Given steps live in
  `tests/conftest.py` under a `config` fixture name kept distinct from the unit tests'
  `unilever_config` fixture to avoid a naming collision between pytest-bdd's dynamic
  step-fixture publishing and the statically-declared fixture.

### Added — Unit test suite (2026-09-27)
- Closes `BACKLOG.md` Phase 8's unit-test item (BDD still open). 36 `pytest` tests under
  `tests/` covering `hyperinflation_calculations.py` (World A/B/C math, the monetary-
  gain/loss balancing-plug identity verified to float precision, and a regression test
  that `build_model()` on the real `unilever` config still reproduces the disclosed 2024
  figures within tolerance), `config_loader.py`'s validation error paths, and the
  pure-Python report stages (`data.py`, `validation.py`, `recommendation.py` — not the
  `claude -p`-driven ones). `requirements-dev.txt` + `pytest.ini` added; verified
  clean-install-to-green in a fresh venv.
- One test's premise was wrong on first run (assumed zero monetary gain/loss follows
  from flat FX/inflation alone, for any input) — the failure was real, traced to why
  (the plug also depends on the fixture being a cash-flow-consistent roll-forward), and
  fixed by correcting the assertion plus adding a second test with an algebraically-
  solved self-consistent fixture proving the zero-plug property when the premise holds.

### Changed — Rewrote git history to remove personal/third-party content (2026-09-27)
- Closes `BACKLOG.md` Phase 6. Removed `.recall/` (a session-history capture directory
  containing raw session transcripts with the repo owner's real machine paths/username)
  and `colossal-visuals/` (an unrelated earlier project, plus a `references/` folder of
  downloaded third-party Excel templates) from every commit via `git-filter-repo
  --invert-paths --path .recall --path colossal-visuals`, then force-pushed. Verified with
  a full tree scan across all 31 rewritten commits and an independent check of the pushed
  remote tree — zero trace of either path anywhere in history. `.recall/` added to
  `.gitignore`. `examples/Blu Containers Model - Vertical Complete.xlsx` (the repo owner's
  own coursework, unrelated to the removed `references/` folder) is untouched.

### Verified — First live run of the equity-report pipeline's claude-p stages, hyperinflation domain (2026-09-27)
- Closes `BACKLOG.md` Phase 4. `REPORT=1 ./scripts/launch.sh unilever` (with `TICKER`/
  `EXCHANGE` added to `examples/unilever/config.py`) — Stages 2 (price/consensus
  research), 4 (section drafting), 5/5.5 (review + coherence gate) all ran live for the
  first time on this domain. Completed successfully end-to-end, producing both
  `Unilever_Hyperinflation_Financial_Model.xlsx` and an 8-section, ~3,900-word
  `Unilever_Hyperinflation_Equity_Research_Report.pdf` in `output/2026-09-27_142024/`.
- Stage 2 found real analyst consensus (TipRanks "Moderate Buy", 10 analysts, 5,080p
  target vs. a 4,664.50p close) and confirmed — the report's central market-perception
  question — that public commentary does not distinguish the IAS 29 net monetary effect
  from ordinary FX-headwind language anywhere it could find. Stage 3's mechanical signal
  ("Flag: immaterial" — net monetary loss is 2.3% of group operating profit, below the
  10% threshold) drove Stage 4's Recommendation section to a correctly-reasoned **Hold**.
- The Stage 5.5 coherence gate converged after 5 iterations (8 → 5 → 4 → 0 findings),
  catching real issues: a drafted section attributing Argentina's monetary loss to
  "holding too many exposed monetary assets" when the model has Argentina as a net
  monetary *liability* that still books a loss (independently rediscovering the same
  subtlety `research_output.md` had already flagged as non-obvious); a misattributed
  share-price source; an unsupported moat rating with no basis in any source file;
  internal pipeline jargon leaking into report prose; and a flag that the group totals
  behind the 2.3% materiality ratio are ~95% illustrative scale, not Unilever's real
  consolidated accounts — fixed by adding an explicit caveat rather than overstating
  precision.
- Stage 0 (sourcing) wasn't re-run — `unilever` was already onboarded from the prior
  session's calibration work.

### Changed — Pivoted repo to a Unilever hyperinflation-accounting teaching model (2026-09-27)
- Closes `BACKLOG.md` Phases 1-3. Full pivot away from the REIT valuation model (Acorn
  I-REIT) to a CFA Level II Financial Statement Analysis teaching model — the
  *Multinational Operations*/IAS 29 hyperinflation-accounting reading — illustrated with
  Unilever plc's real disclosed Argentina/Türkiye subsidiary treatment. Deleted REIT/bank
  cruft: `examples/acorn_i_reit/`, `reit_calculations.py`/`reit_excel_renderer.py`,
  `build_reit_model.py`, the stale root `research_output.md` (leftover Family Bank Kenya
  data, pre-REIT), and `TODO.md`/`Modelling_Instructions.md`/`Using_modeleon.md` (stale
  bank-era docs describing an unused `modeleon` DSL, confirmed via repo-wide grep).
- New `bizplan/financial/hyperinflation_calculations.py`: a World A (plain current-rate)
  / World B (US GAAP temporal/remeasurement) / World C (actual IFRS — IAS 29 restatement
  + IAS 21 closing-rate translation) engine, net monetary gain/(loss) computed as a
  balancing plug per subsidiary per year. Argentina + Türkiye 2024 local-currency inputs
  solved **algebraically** (not trial-and-error — see `examples/unilever/
  research_output.md`'s "Calibration method") to reproduce Unilever's real disclosed 2024
  IAS 29 impact table (Total assets/Turnover/Operating profit/Net monetary gain-loss, both
  subsidiaries) to within rounding. Rolled the calibrated model forward into 2025 (not
  re-solved) as an out-of-sample validation: 3 of 4 impact lines correctly flip to the real
  disclosed sign for both subsidiaries; total-assets impact structurally cannot (pure
  inflation restatement can only raise local non-monetary values — documented as an open,
  undocumented-by-source limitation, not forced to match).
- New `bizplan/financial/hyperinflation_excel_renderer.py`: fully formula-linked workbook
  (Cover, Assumptions, `Argentina_Schedules`/`Turkiye_Schedules` each walking Local FS →
  Inflation Index → IAS 29 Restatement → FX Translation → World A/B/C → IAS 29 Impact,
  Consolidation, `Scenario_Comparison` showing World A/B/C **side by side** per the user's
  own requested shape — a deliberate deviation from the REIT model's single-scenario
  `CHOOSE()` switch, since comparing all three simultaneously is the point here — plus
  Validation_2025, Sources). Verified with the `formulas` Python package (an independent
  Excel-formula evaluator): every schedule-sheet figure matches the Python engine exactly,
  zero formula errors anywhere in the workbook.
- `bizplan/config_loader.py` rewritten for the new schema (`SUBSIDIARIES`,
  `INFLATION_INDICES`, `FX_RATES`, `ACCOUNTING_SCENARIOS`, `VALIDATION_ACTUALS`, ...).
  `scripts/build_unilever_model.py` (replacing `build_reit_model.py`), launch
  scripts updated; smoke-tested end-to-end via `./scripts/launch.sh unilever`.
- `bizplan/report/*` (the equity-research-report pipeline) adapted to this domain:
  `data.py`'s `company_facts()`/`monetary_exposure_grades()` replace REIT valuation-per-
  unit/financial-health fields; `validation.py` now gates on **calibration fidelity**
  (does the model still reproduce the real disclosed figures?) rather than a
  tautological balance check (net monetary gain/loss is solved as the exact plug that
  makes the restated balance sheet tie out, by construction — see the module docstring);
  `recommendation.py`'s mechanical pre-decision is now a materiality flag (|net monetary
  gain/loss| ÷ group operating profit vs. a 10% threshold) rather than a NAV/DDM/Cap-Rate
  Buy/Hold/Sell call, since this model doesn't build a full equity valuation — verified
  against the calibrated instance: comes back "Flag: immaterial" (~2% of Unilever's real
  group operating profit), a genuine finding (dramatic at the subsidiary level, immaterial
  at Unilever's actual size), not a bug. `pdf.py`'s charts/tables replaced accordingly
  (World A/B/C comparison, per-subsidiary IAS 29 impact, 2025 validation gap,
  monetary-exposure grades) — verified with a real generated test PDF. All 8 section SOPs
  under `.devops/agents/equity-report/` rewritten from REIT language to this domain
  (investment thesis, bulls/bears, economic moat, valuation/scenarios, financial health,
  market consensus, recommendation, risks), plus `model-sourcing.md` and
  `price-consensus-research.md`; `coherence-apply-fixes.md` needed no changes.
- Full deterministic-stage smoke test (Stage 1/1b → Excel build → Stage 3 → Stage 6 PDF)
  ran end-to-end without errors. `claude -p`-driven stages (0, 2, 4, 5, 5.5) not yet run
  live — tracked as `BACKLOG.md` Phase 4. BBVA/Garanti "advanced case" explicitly deferred
  as `BACKLOG.md` Phase 5, per the user's own sequencing.
- `BLUEPRINT.md`, `BACKLOG.md`, `README.md`, `AGENTS.md`, `CLAUDE.md` rewritten for the
  new domain.

### Verified — First live run of the equity-report pipeline's claude-p stages (2026-09-04)
- Closes `BACKLOG.md` Phase 2's last open item. `python scripts/generate_equity_report.py
  acorn_i_reit --output-dir <dir> --ticker "ASA I-REIT" --exchange "NSE Unquoted
  Securities Platform"` — Stages 2 (price/consensus research), 4 (section drafting), 5/5.5
  (review + coherence gate) all ran live for the first time (Stage 0 sourcing wasn't
  re-run; Acorn was already onboarded). Completed successfully end-to-end, producing both
  `Acorn_I-REIT_Financial_Model.xlsx` and a 9-page `Acorn_I-REIT_Equity_Research_Report.pdf`.
- Stage 3's mechanical signal: Hold (High uncertainty, 63.5% method spread). Stage 4 drafted
  all 8 sections, with the analyst overriding to a Buy on a specific, falsifiable catalyst
  (payout-ratio normalization toward the CMA 80% minimum).
- The Stage 5.5 coherence gate did exactly the job it exists for: caught and fixed 6 real
  cross-section inconsistencies over 3 iterations before converging on 0 unresolved
  findings — a price quoted two different ways across sections, a NAV/unit rounding
  mismatch, a peer premium/discount self-contradiction, a thesis section that never
  previewed the eventual Buy call, and two duplicate-metric/different-label collisions.
- Found (not yet fixed): `examples/acorn_i_reit/config.py` has no `TICKER`/`EXCHANGE`
  fields, so those must be passed explicitly on every run. Tracked as a new `BACKLOG.md`
  Phase 3 item.

### Changed — Two-tier seed/stabilized occupancy model, replacing single-glide (2026-09-03)
- Closes `BACKLOG.md` Phase 3's occupancy item. Prompted by a user idea to pull per-property
  detail (rooms/beds/operations-start dates) from the interim report's p.11 "Portfolio
  Update" and model occupancy by regression. Fetched and read the actual PDF directly
  (including rendering p.12's occupancy-trend chart as an image to rule out embedded data
  labels a text-only extraction might miss): confirmed no per-property or continuous
  occupancy series is disclosed anywhere, only a qualitative "seed" (underperforming: Jogoo
  Road/Ruaraka/Parklands) vs. "stabilized typical assets" (the other 4, 93% H1-2025) split —
  so a literal regression wasn't fittable, but the seed tier's own occupancy is legitimately
  back-solvable `[DISCLOSED-DERIVED]` from the two disclosed aggregates (portfolio-blended,
  stabilized-tier), bed-weighted, for both H1-2024 (80.7%) and H1-2025 (59.0%) -- a real
  decline, not a maturity story.
- **Caught and corrected my own initial framing**: operations-start dates disprove an
  age/maturity-driven split -- Jogoo Road (2017, oldest) is "seed", Aberdare Heights II
  (2022, newest) is already "stabilized". Documented explicitly so a future regression
  attempt against property age isn't tried again.
- `config.py`: `PROPERTIES` entries gain `tier` (seed/stabilized) and `operations_start`
  fields; `RENTAL_INCOME` gains H1-2024 comparative occupancy figures.
  `bizplan/config_loader.py` validates `tier` is present and one of the two allowed values.
  `reit_calculations.py` adds `compute_tier_beds()`, `compute_seed_occupancy()` (generic
  back-solve), `compute_seed_occupancy_h1_2024/2025()`; `build_rental_income_noi()` now
  models the two tiers separately (stabilized flat at the scenario-flexed target, seed
  glides toward it) before bed-weighting back into one portfolio figure.
- `reit_excel_renderer.py`: the Model sheet's occupancy row was previously an
  *independently* hand-written Excel formula (not derived from the Python change at all) --
  replaced with 3 live-formula rows (Seed tier / Stabilized tier / blended portfolio), plus
  a new Assumptions-sheet row for the back-solved seed occupancy and a Tier/Operations-start
  column on the Property Portfolio table. Cross-verified with the `formulas` package (a real
  Excel-formula evaluator) that the rendered workbook matches the Python ground truth exactly
  across Base/Best/Worst scenarios, and the Master Check still reads OK for Balance
  Sheet/LTV/Income-Producing across all 24 year×scenario combinations (Payout ERROR for
  2023-2025 actuals is unchanged, documented, correct-by-design behavior).
- That verification pass caught a real latent bug predating this change: the old
  single-tier Excel formula never capped occupancy at 100% (only Python did), so an extreme
  Best-case scenario could show >100% occupancy in the rendered workbook. Fixed by capping
  the scenario-flexed target reference in both new tier formulas.
- Base-case blended occupancy numbers are numerically unchanged from the prior design (a
  mathematical necessity: bed-weighting "flat at target" with "linear glide to the same
  target" is itself a linear glide from the same start to the same target) -- the real gains
  are correct provenance, more realistic Best/Worst ceiling behavior, and exposing the
  back-solved seed occupancy as its own documented figure. Also fixed a prior unsourced 0.85
  placeholder for 2024's displayed actual occupancy to the disclosed 0.88; 2023's unsourced
  0.78 is left as a flagged, not-yet-sourced placeholder.

### Added — Comparative REIT actuals + sector cap-rate cross-check research (2026-08-25)
- Closes `BACKLOG.md` Phase 3's cap-rate item; partially advances the "extend to a second
  REIT instance" item (sourcing done for 2 of 4 candidates). Five parallel research passes
  against `research_output.md`'s own "Not yet pulled" gaps:
  - **LAPTRUST Imara I-REIT**: sourced 3 full years of audited actuals (FY2023-25) directly
    from NSE-hosted filings — corrects the prior "three consecutive loss years" assumption
    (actually two, FY2024-25; FY2023 was profitable) and finds it's fully ungeared with a
    clean 80.0% payout every year, a sharp contrast to Acorn.
  - **ILAM Fahari I-REIT**: sourced FY2025 audited (+FY2024 comparative) directly from its
    investor-relations site, including its independent valuer's Note 11 unobservable-inputs
    table (retail/office term & reversionary yields) — the best-sourced formal cap-rate
    cross-check found anywhere in this research.
  - **ALP Industrial REIT**: sourced its maiden H1 2026 interim (USD-denominated, listed
    Mar-2026, no full-year report exists yet) — property-level detail with disclosed entry
    yields (8.17%-9.26%).
  - **TRIFIC Green USD I-REIT**: confirmed not yet sourceable — listed Jun-2026, no
    annual/interim report published; only prospectus projections found, correctly not
    treated as disclosed actuals.
  - **Sector cap rate**: no single authoritative Kenya REIT cap rate is published; sourced
    segment-level yields instead (Cytonn/Knight Frank Nairobi residential 5.4%-7.4%, ILAM
    Fahari's own disclosed retail/office yields, ALP Industrial's disclosed industrial entry
    yields) and cross-checked against Acorn's own implied 5.47% `cap_rate` — falls
    comfortably within the general residential range. No `config.py` valuation figures
    changed; this is citation/cross-check documentation only (`config.py` `SOURCES` list and
    the `cap_rate` comment updated to point at it).
- All findings tagged `[DISCLOSED]`/`[DISCLOSED-DERIVED]` with source URLs in
  `research_output.md`'s new 2026-08-25 section; gaps (e.g. LAPTRUST/ALP per-property detail,
  ILAM Fahari's/TRIFIC's trading price) reported honestly rather than filled with estimates.

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
