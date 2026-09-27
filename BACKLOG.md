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
