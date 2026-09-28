# BACKLOG — Unilever Hyperinflation-Accounting Model

Tracks status against `BLUEPRINT.md`. Check items off as they land; append the
corresponding entry to `CHANGELOG.md` when you do. This is the "what's next" doc — read it
first to know what's next.

The prior REIT-model backlog (Phases 1-2) is preserved in git history for anyone tracing
why a particular piece of shared infrastructure (`xl_helpers.py`, the config-loader
pattern) looks the way it does — not reproduced here, since none of the REIT-specific
schedule/valuation work applies to this domain.

---

## Phase 1 — Pivot repo to the Unilever hyperinflation-accounting model (2026-09-27) — DONE

- [x] Deleted REIT/bank cruft: `examples/acorn_i_reit/`,
      `bizplan/financial/reit_calculations.py`/`reit_excel_renderer.py`,
      `scripts/build_reit_model.py`, root `research_output.md` (stale Family Bank Kenya
      leftover), `TODO.md`/`Modelling_Instructions.md`/`Using_modeleon.md` (stale
      bank-era docs describing an unused `modeleon` DSL — confirmed via repo-wide grep
      that it's never imported anywhere in `bizplan`).
- [x] `bizplan/config_loader.py` rewritten: new `REQUIRED_FIELDS` (`SUBSIDIARIES`,
      `INFLATION_INDICES`, `FX_RATES`, `ACCOUNTING_SCENARIOS`, `VALIDATION_ACTUALS`, ...),
      `validate_config()` replacing `validate_reit_config()`.
- [x] `bizplan/financial/hyperinflation_calculations.py` — new pure-Python engine:
      `restate_and_translate()` (World A/B/C from local nominal inputs, net monetary
      gain/loss as a balancing plug), `consolidate()`, `scenario_comparison_table()`,
      `validate_against_disclosed()`, `build_model()` (single entry point). Calibrated
      Argentina + Türkiye 2024 local-currency inputs solved **algebraically** (not
      trial-and-error) to reproduce Unilever's real disclosed 2024 IAS 29 impact table to
      within rounding — verified both in pure Python and via the rendered Excel
      workbook's live formulas (cross-checked with the `formulas` package, an independent
      Excel-formula evaluator; zero error cells).
- [x] `examples/unilever/config.py` + `research_output.md` — calibrated subsidiary
      inputs, full algebraic derivation, real disclosed 2024/2025 figures with SEC EDGAR
      citations, and an explicit "what this model is and isn't" section (this is a
      fictional-but-reconciling illustration, not a reproduction of Unilever's actual
      subsidiary financial statements — those aren't publicly disclosed at this
      granularity).
- [x] `bizplan/financial/hyperinflation_excel_renderer.py` — full formula-linked
      workbook (Cover, Assumptions, `Argentina_Schedules`/`Turkiye_Schedules` each
      walking the full 01→04 restatement chain plus World A/B/C, Consolidation,
      Scenario_Comparison showing World A/B/C side by side, Validation_2025, Sources).
      Verified end-to-end with the `formulas` package: every schedule-sheet impact figure
      matches the Python engine's output exactly, zero formula errors anywhere in the
      workbook.
- [x] `scripts/build_unilever_model.py` (replacing `build_reit_model.py`), `--instance`
      flag (was `--reit`), default instance `unilever`. `scripts/launch.sh`/`.bat`/`.ps1`
      updated to match; smoke-tested end-to-end via `./scripts/launch.sh unilever`.
- [x] `BLUEPRINT.md`, `BACKLOG.md` rewritten for the new domain (this file). `README.md`,
      `CLAUDE.md`, `AGENTS.md` reframed. `CHANGELOG.md` appended (not rewritten — it's an
      explicit running log).

## Phase 2 — 2025 out-of-sample validation (2026-09-27) — DONE, gap documented

- [x] Rolled the calibrated 2024 model forward into 2025 with updated (not re-solved)
      macro assumptions reflecting real events — Argentina's April-2025 currency float
      (reversing 2024's "inflation outpaces FX" relationship) and Türkiye's continued
      lira depreciation against decelerating inflation. Result: **3 of 4 impact lines
      correctly flip to the real disclosed sign** for both subsidiaries (turnover,
      operating profit, net monetary gain/loss); **total-assets impact does not**, and
      `research_output.md` documents the structural reason why (pure inflation
      restatement can only raise local non-monetary asset values — it can't produce a
      negative impact once translated at a shared closing rate, regardless of FX). Real
      Unilever's negative 2025 total-assets impact likely reflects an effect (disposals,
      impairments, a different comparative-basis convention) not visible from the
      four-line summary table alone — flagged as an open, undocumented-by-source
      limitation rather than forced to match.
- [x] Found and documented that Türkiye's 2025 same-sign match required an explicit
      margin-recovery assumption (the underlying business turning profitable), not a pure
      mechanical roll-forward — see research_output.md's "Why Türkiye 2025 assumes margin
      recovery" for the algebraic reason (a World-A operating *loss* times a
      sign-flipped inflation-vs-FX wedge produces the wrong-signed impact otherwise).

## Phase 3 — Adapt `bizplan/report/*` (equity-research-report pipeline) to this domain (2026-09-27) — DONE (deterministic stages)

- [x] `sourcing.py`/`pipeline.py` swapped `reit_calculations`/`reit_excel_renderer`
      imports for `hyperinflation_calculations`/`hyperinflation_excel_renderer`. Dropped
      the REIT pipeline's "as-of anchor year" rolling-forecast framing from Stage 0/
      `scripts/source_model.py`/`scripts/refresh_report.py` — this model is a fixed
      two-year calibration+validation exercise, not a multi-year forecast to re-anchor
      each quarter; `source_model()` is now a verification/refresh pass.
- [x] `bizplan/report/data.py` rewritten: `company_facts()` now reads consolidated
      World-C total assets/revenue/operating profit/net monetary gain-loss for the
      primary year; new `monetary_exposure_grades()` (documented |net monetary
      gain-loss|/total-assets banding, A-F) replaces the REIT model's LTV/income-
      producing/payout `financial_health_grade()` — there's no regulatory-buffer concept
      in this domain, but a balance-sheet monetary-exposure read is a real analogous
      signal. `to_report_json()` now surfaces `ias29_impact_primary_year`,
      `scenario_comparison`, `validation_gap`, `monetary_exposure` instead of REIT
      valuation-per-unit/scenario/sensitivity blocks.
- [x] `bizplan/report/validation.py` rewritten: gates on **calibration fidelity** (does
      the model's primary-year output still reproduce the real disclosed impact figures
      within ±0.5 EURm?) rather than a Balance-Sheet-Check-style identity — documented in
      the module docstring why a balance check would be tautological here (net monetary
      gain/loss is solved as the exact plug that makes the restated balance sheet tie
      out, by construction, not an independently-forecast figure that could disagree).
- [x] `bizplan/report/recommendation.py` rewritten: a materiality flag (|net monetary
      gain/loss| ÷ |group operating profit| vs. a documented 10% threshold) replaces the
      REIT pipeline's NAV/DDM/Cap-Rate-blend Buy/Hold/Sell mechanical pre-decision — this
      model doesn't build a full equity valuation, so Stage 3's job here is narrower and
      honest about that scope. Verified against the calibrated `unilever` instance: comes
      back "Flag: immaterial" (net monetary loss is only ~2% of Unilever's real-scale
      group operating profit) — a genuine, sensible finding, not a bug: dramatic at the
      subsidiary level, immaterial at Unilever's actual group size.
- [x] `bizplan/report/pdf.py` rewritten: replaced the REIT valuation-methods/sensitivity/
      scenario charts and peer-REIT table with a World A/B/C operating-profit comparison
      chart, a per-subsidiary IAS 29 impact bar chart, a 2025 model-vs-disclosed
      validation-gap chart, and a monetary-exposure grade table. Verified: a test PDF
      built successfully (111KB, all three charts + table rendered) from fabricated
      section content.
- [x] All 8 section SOPs under `.devops/agents/equity-report/` rewritten from REIT
      language to this domain: investment thesis (subsidiary exposure + earnings-quality
      signal), bulls/bears (updated JSON field references), economic moat (local
      pricing-power/monetary-exposure-discipline lens), valuation/scenarios (World A/B/C
      narration), financial health (monetary-exposure grades), market consensus (does it
      distinguish IAS 29 from ordinary FX?), recommendation (earnings-quality-mispricing
      decision logic, not a price-vs-fair-value call), risks (model-limitation risk
      stated plainly). `price-consensus-research.md` and `review-plagiarism-references.md`
      updated field references; `coherence-apply-fixes.md` needed no changes (already
      domain-agnostic).
- [x] Full deterministic-stage smoke test: Stage 1/1b (ground truth + validation) → Excel
      build → Stage 3 (materiality flag) → Stage 6 (PDF, with fabricated section content
      standing in for Stage 4/5) ran end-to-end without errors.

## Phase 4 — Live run of the `claude -p`-driven stages (2, 4, 5, 5.5) — DONE (2026-09-27)

- [x] `REPORT=1 ./scripts/launch.sh unilever` (ticker `ULVR`/exchange `LSE` added to
      `examples/unilever/config.py` for Stage 2). Stage 0 (sourcing) wasn't re-run —
      `unilever` was already onboarded. Ran successfully end to end, producing both
      `Unilever_Hyperinflation_Financial_Model.xlsx` and a `report_reviewed.md`
      (~3,900 words across 8 sections)-based `Unilever_Hyperinflation_Equity_Research_
      Report.pdf` (132KB) in `output/2026-09-27_142024/`.
- [x] Stage 2 (live web research): found real analyst consensus (TipRanks "Moderate Buy",
      10 analysts, 5,080p target; Trading Economics 4,664.50p close) and confirmed via
      call transcripts/6-K filings that public commentary does **not** separate the
      IAS 29 net monetary effect from ordinary FX-headwind language — exactly the
      market-perception question this report was built to test.
- [x] Stage 3 mechanical signal: **"Flag: immaterial"** (net monetary loss −€195m is
      2.3% of group operating profit €8,496m, below the 10% threshold) → Stage 4's
      Recommendation section correctly called **Hold**, reasoned on size (not on the
      market having priced it correctly).
- [x] Stage 5.5's coherence gate did exactly the job it exists for: converged after
      **5 iterations** (8 → 5 → 4 → 0 findings), catching real cross-section issues
      including one this repo's own `research_output.md` had flagged as a subtle,
      easy-to-get-wrong point — Stage 5 independently caught a drafted section wrongly
      attributing Argentina's monetary loss to "holding too many exposed monetary
      assets" when the model actually has Argentina as a net monetary *liability* that
      still books a loss (equity/profit restatement growth outweighs it). Also caught: a
      misattributed share-price source, an unsupported "Wide/Narrow/None" moat rating
      with no basis in any source file, an internal-pipeline-jargon leak ("Stage 2
      research", "Sell-leaning/Caution") into report prose, and an inconsistent framing
      of whether the market "may be mispricing" the effect vs. it being immaterial.
- [x] Found (not a bug, a real finding): the review flagged that the group totals used
      for the 2.3% materiality ratio are ~95% the illustrative `OTHER_GROUP_OPERATIONS_
      EUR` scale, not Unilever's real reported consolidated accounts — Stage 4's fix
      added an explicit caveat to the Recommendation section rather than overstating the
      ratio's precision. A good example of the coherence gate catching a scope-honesty
      issue the SOPs didn't explicitly anticipate.

## Phase 5 — BBVA/Garanti "advanced case" — NOT STARTED, deferred by design

BBVA applies IAS 29 to both its Türkiye (Garanti BBVA) and Argentina (BBVA Argentina)
subsidiaries; unlike Unilever, Garanti BBVA separately publishes its own full IFRS
financial statements, which would let a future pass attempt an **actual** subsidiary-to-
parent reconstruction rather than a calibrated fictional one. Explicitly out of scope for
this pass per the user's own sequencing (`Unilever 2024` → learn the mechanics;
`BBVA/Garanti` → prove they apply to real subsidiary statements) — do not start without
confirming scope first, same as any new phase.

## Phase 6 — Repo hygiene: remove personal/third-party content from git history (2026-09-27) — DONE

- [x] Found `.recall/` (a 716KB session-history capture directory containing raw
      Claude Code session transcripts, including the repo owner's real Windows machine
      paths/username) tracked in git and already pushed to the public remote. Removed
      from the working tree, added to `.gitignore`.
- [x] Found an entire unrelated earlier project ("colossal-visuals", an LED-screen/
      concert pitch-deck generator with stock photography) plus a `references/` folder
      of **downloaded third-party Excel templates** (`CashFlVl.XLS`, `Due-Diligence-
      Assessment.xls`, `Ethos_360_Break-Even_Forecaster.xls`, `Financial_model_1.xls`,
      `Ratio_Tree.xls`, `sample_business_plan.pdf`) bundled into the very first commit —
      already removed from the working tree in an old commit, but still fully
      recoverable from git history on the public remote.
- [x] Rewrote git history with `git-filter-repo --invert-paths --path .recall --path
      colossal-visuals` (all 31 commits preserved, just stripped of those paths) and
      force-pushed. Verified via a full tree scan across every rewritten commit
      (`git rev-list --all | xargs git ls-tree -r --name-only`) and an independent check
      of the pushed remote tree via `gh api` — zero trace of either path anywhere in
      history. `Blu Containers Model - Vertical Complete.xlsx` (the repo owner's own FMI
      coursework, confirmed, kept) is unaffected — it lives under `examples/`, not the
      removed `colossal-visuals/references/` path.

## Phase 7 — Peer-comparison and standard-setting content — DONE (2026-09-27)

- [x] **Peer-comparison section**: added `PEER_COMPARISON` to `examples/unilever/
      config.py` (Coca-Cola FEMSA's Argentina net-monetary-position gain, H1 2025 vs H1
      2024; BBVA's real disclosed Türkiye figures, FY2023 −€2,118m/+€1,202m, FY2022
      −€2,323m/+€1,490m), surfaced through `data.to_report_json()` (optional field, read
      defensively via `getattr` — an institution's config without it still works, see
      test), written up in `research_output.md`'s new "Peer comparison" section with
      citations, and referenced (briefly, only if non-empty) in `section-valuation-
      scenarios.md`'s SOP. Contrasted directly with Unilever's own Argentina in the
      writeup: FEMSA's Argentina is also a net monetary liability position but nets to a
      *gain*, unlike Unilever's — a real, useful illustration of "A finding worth
      flagging." BBVA/Garanti's full subsidiary reconstruction stays Phase 5, deferred.
- [x] **Standard-setting watch note**: added `STANDARD_SETTING_NOTE` to `config.py`
      (the IFRS Interpretations Committee's July 2025 agenda decision on qualitative
      hyperinflation indicators), surfaced the same way, written up in
      `research_output.md`, referenced in `section-risks-uncertainty.md`'s SOP as a
      classification-risk bullet.
- [x] **Bonus, found while in there**: `CONSENSUS` and `VALUATION` in `config.py` were
      still marked `[PLACEHOLDER]` even though the live pipeline run (`BACKLOG.md` Phase
      4) had already confirmed the market-perception hypothesis and produced a real
      recommendation — updated both to state the confirmed finding, with a pointer to
      the full citation trail in `examples/2026-09-27_222102/report_workdir/
      price_consensus_research.json` (the checked-in sample was refreshed on
      2026-09-27 — see the "Replaced the checked-in sample" entry near the end of this
      phase). Also fixed `VALUATION`'s note, which still
      described the old (pre-rewrite) NAV/DDM/cap-rate mispricing-check design instead
      of the current materiality-flag one. Added 3 new tests
      (`tests/test_report_data.py`) covering the new fields, including the optional-field
      default-to-empty path.
- [x] **Extended (2026-09-27, same day, in response to a follow-up)**: added two more
      real peers to `PEER_COMPARISON` after the user asked whether a true household-goods
      peer existed — **Colgate-Palmolive** (US GAAP filer; names Argentina/Türkiye/Nigeria
      "highly inflationary" and discloses no dollar impact because it judges the effect
      immaterial — a real-world instance of this model's own "Flag: immaterial"
      conclusion for Unilever, reached independently under ASC 830/the temporal method,
      i.e. real-world **World B** in production) and **Reckitt Benckiser** (IFRS filer,
      same IAS 29 regime as Unilever, but discloses hyperinflation bundled into one
      "Exchange and hyperinflation" LFL reconciling item rather than a separate net-
      monetary line — and fully divested its Argentina business on 31 Dec 2025 as part of
      a £2.2bn "Essential Home" segment sale). Found by fetching and reading the actual
      10-K/annual-report PDFs directly (not just search snippets) — search alone didn't
      surface either figure. `research_output.md` frames these honestly as a disclosure-
      granularity contrast, not a clean number-matching table, since neither peer
      discloses a figure directly comparable to Unilever's or BBVA's. Updated
      `section-valuation-scenarios.md`'s SOP and the existing peer-comparison test.
- [x] **Replaced the checked-in sample with a fresh full live run (2026-09-27, later the
      same day)**: `REPORT=1 ./scripts/launch.sh unilever` re-run end to end now that
      `config.py` carries the peer-comparison and standard-setting content — Stage 4's
      drafted sections correctly pulled in the new Colgate/Reckitt/BBVA/IFRS-IC material
      (confirmed live, not assumed). The coherence gate used its full 10-iteration budget
      this run (converging to 0 unresolved findings on the last one, not a QA-flags
      ship) — genuinely more issues to catch with more cited material in play, including
      good catches like a moat-rating headline contradicting its own per-market verdict
      and Recommendation contradicting its own Hold call. Deleted the old
      `examples/2026-09-27_142024/` sample and replaced it with
      `examples/2026-09-27_222102/`; regenerated `docs/screenshots/*.png` from the new
      PDF; updated every current-state doc pointer (`README.md`, `AGENTS.md`,
      `research_output.md`, `config.py`) to the new path — `CHANGELOG.md`'s own
      historical "First live run" entry describing the old path is left untouched, since
      it's an accurate record of what actually happened then, not a live pointer.

## Phase 8 — Testing: unit tests + BDD — DONE (2026-09-27)

- [x] **Unit tests** (`pytest`, under `tests/`, `pytest.ini` + `requirements-dev.txt`) for
      `bizplan/financial/hyperinflation_calculations.py` (36 tests total; the World A/B/C
      math under flat and inflated macro conditions, the monetary-gain/loss plug's exact
      balancing-identity property verified to float precision, a dedicated regression
      test that `build_model()` on the real `examples/unilever/config.py` reproduces
      Unilever's disclosed 2024 figures within ±0.01 EURm), `bizplan/config_loader.py`
      (`validate_config()`'s error paths — missing fields, empty `YEARS`, malformed
      `SUBSIDIARIES`/`ACCOUNTING_SCENARIOS`/`INFLATION_INDICES` — via real `tmp_path`
      config files exercising the actual import machinery, not hand-built namespaces),
      and `bizplan/report/{data,validation,recommendation}.py` (pure-Python stages only,
      not the `claude -p` ones — includes a test that deliberately breaks calibration by
      mutating `ACTUALS` and confirms `validate_model()` catches it, not just that the
      happy path passes). Verified clean-install-to-green in a fresh venv from
      `requirements-dev.txt` alone. One test's own premise was initially wrong (assumed
      "flat FX/inflation implies zero monetary gain/loss" for an arbitrary fixture) —
      caught by running it, fixed by understanding *why* (the plug depends on the
      fixture being a cash-flow-consistent roll-forward, not on flatness alone) rather
      than loosening the assertion; a second test added alongside it using an
      algebraically-solved self-consistent fixture to prove the zero-plug property does
      hold when the premise is actually met.
- [x] **BDD** (`pytest-bdd`, chosen over `behave` for a single `pytest` runner shared
      with the unit tests — same command, same fixtures, same CI hook) — 3 feature
      files under `tests/features/`, 15 scenarios total:
      1. `calibration.feature` — *code behavior*: a Scenario Outline (8 examples,
         Argentina/Türkiye × all 4 impact metrics) asserting the model reproduces
         Unilever's real disclosed 2024 figures, plus a scenario confirming a
         deliberately-broken calibration is caught, not silently accepted. A
         Gherkin-readable version of the calibration-fidelity check `validation.py`
         already does, executable by a non-engineer reviewer.
      2. `recommendation.feature` — the materiality-threshold decision logic
         (immaterial/material cases) plus the real calibrated Unilever case.
      3. `report_data_generation.feature` — *output-generation behavior*, scoped (as
         planned) to the deterministic stages only: the generated report JSON carries a
         scenario comparison for every World and a monetary-exposure grade for every
         subsidiary, and the mechanical recommendation reads figures consistent with
         that same JSON. No live `claude -p` calls — the LLM-drafted sections stay out
         of scope for this feature, exactly as planned before writing feature files.
      Shared steps ("Given the calibrated Unilever configuration") live in
      `tests/conftest.py`, published under a `config` fixture name distinct from the
      plain-pytest `unilever_config` fixture to avoid a fixture-name collision between
      pytest-bdd's dynamic step-fixture publishing and the statically-declared one.

## Phase 9 — Documentation and tooling improvements — DONE (2026-09-27)

- [x] **README summary section**: added a short section to `README.md` naming the
      repo's technical scope and verification status — later folded into the sections
      that already covered the same facts (Calibration, Running the tests, `AGENTS.md`'s
      verification status) rather than duplicating them in a standalone list
      (2026-09-28).
- [x] **Embedded screenshots/preview in README**: two PNGs rendered from the checked-in
      sample PDF (`examples/2026-09-27_222102/...Equity_Research_Report.pdf`) via
      PyMuPDF, cropped to content (`docs/screenshots/report_cover.png`,
      `report_charts.png`) and embedded near the top of `README.md`.
- [x] **CI that verifies calibration on every push**: `.github/workflows/tests.yml` —
      installs `requirements-dev.txt`, runs the full `pytest` suite (which includes the
      calibration-fidelity regression test from Phase 8), then builds the Excel model as
      an end-to-end smoke test, on every push/PR to `main`.
- [x] **Interactive World A/B/C demo**: `scripts/build_interactive_demo.py` generates a
      single self-contained `docs/demo/index.html` (no external scripts, no server,
      works via `file://`) with the real model's data embedded inline — toggle buttons
      for World A/B/C update cards (Revenue/Operating Profit/Total Assets/Net Monetary
      Gain-or-Loss/ROA/Asset Turnover), a permanent bar-chart comparison across all
      three worlds, and the per-subsidiary IAS 29 impact table. Chose a plain repo file
      over a Claude Artifact so it's a durable, portable asset that travels with the
      repo itself. Verified by hand (brace-balance and script-tag-count checks, careful
      line-by-line JS read, cross-checked every `DATA.worlds[w].X` access against the
      generator's actual output keys) — no browser tooling was available this session to
      render it directly.

## Phase 10 — Repo hygiene, round 2: license headers + git identity + LICENSE (2026-09-28) — DONE

- [x] **MIT license headers**: `scripts/add_license_headers.py` — idempotent, walks
      `bizplan/`, `scripts/`, `tests/`, and `examples/unilever/config.py` (deliberately
      excludes timestamped sample-run directories under `examples/`, since those are
      frozen output snapshots, not authored source — same reasoning as everywhere else
      in this repo that snapshots aren't hand-edited). Inserts a one-line
      `# Copyright (c) 2026 Edwin Njeru. Licensed under the MIT License (see LICENSE).`
      after any shebang, before any module docstring. Applied to all 37 first-party `.py`
      files. Caught its own edge case: the script's `HEADER` string constant contains the
      marker text as data, so on its first run the script mistook itself for
      already-licensed and skipped itself — fixed by hand-adding its own header rather
      than complicating the detection logic for one self-referential case.
- [x] **LICENSE**: added MIT, referenced from `README.md`.
- [x] **Commit author identity, properly this time**: found the earlier Phase 6 rewrite
      hadn't covered every identity variant — a second local-hostname email
      (`edwin@Apples-MacBook-Pro.local`) and two different name-formats of the real Gmail
      were still scattered across history. Rewrote all 39 commits via `git-filter-repo
      --mailmap` to one consistent identity (`Edwin Njeru
      <20181639+ghacupha@users.noreply.github.com>`, GitHub's privacy-preserving noreply
      address, not the personal Gmail), then set that as this repo's local git config so
      future commits match automatically. Hit a real snag: `git-filter-repo` prompted an
      interactive Y/N question about continuing from the prior day's filter-repo run, and
      the first backgrounded attempt hung over an hour because stdin had nothing to
      answer it with — killed the hung process, confirmed via `git fsck` and `git status`
      that nothing was corrupted, then reran it correctly. Verified the final state via
      the GitHub API, not just local git.

## Phase 11 — Remove Blu Containers Model reference file (2026-09-28) — DONE

- [x] `examples/Blu Containers Model - Vertical Complete.xlsx` (kept through Phase 6 as
      the repo owner's own FMI coursework, safe to keep at the time) reconsidered: fine
      for private/employer viewing, but its copyright status isn't clear enough for
      public redistribution. Removed from the working tree and purged from every commit
      via `git-filter-repo --invert-paths --path-glob '*Blu Containers*'`, then
      force-pushed. Verified via a full tree scan across every rewritten commit and an
      independent check of the pushed remote tree — zero trace anywhere in history.
