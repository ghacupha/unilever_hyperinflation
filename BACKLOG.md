# BACKLOG — REIT Valuation Model

Tracks status against `BLUEPRINT.md`. Check items off as they land; append the
corresponding entry to `CHANGELOG.md` when you do. This is the "what's next" doc — read it
first to know what's next.

The prior banking-model backlog (Phases 1-24-ish) is preserved in git history for anyone
tracing why a particular piece of shared infrastructure (`xl_helpers.py`, the
config-loader pattern, the CHOOSE-switch scenario architecture) looks the way it does —
not reproduced here, since none of the bank-specific schedule/valuation work applies to
the REIT domain.

---

## Phase 1 — Pivot repo to generic REIT valuation model, first instance Acorn I-REIT (2026-08-09) — DONE

- [x] Research: CMA I-REIT regulatory limits (gearing 35%/40%, income-producing minimum
      75%, distribution minimum 80%, min initial assets), Acorn I-REIT's own H1 2025
      interim financial statements (full P&L/BS/cash flow/equity roll-forward, 17 notes),
      the sector-wide equity analysis report's FY2025 headline figures, standard REIT
      valuation methodology (NAV/DDM/cap-rate/multiples). See
      `examples/acorn_i_reit/research_output.md`.
- [x] `bizplan/config_loader.py` — REIT `REQUIRED_FIELDS` + `validate_reit_config`,
      replacing the bank schema.
- [x] `examples/acorn_i_reit/config.py` + `research_output.md` — calibrated from real
      disclosures, provenance-tagged, including two documented reconciliation gaps in the
      source filing itself (units-in-issue vs. reported NAV/unit; Note 17's internally
      inconsistent Dec-2024 mini-table vs. the primary Statement of Changes in Equity).
- [x] `bizplan/financial/reit_calculations.py` — Python ground truth for every schedule
      (property portfolio, rental/NOI, opex, debt, income statement, distributable
      income, units, balance sheet, regulatory compliance, ratio disclosures, valuation),
      plus Base/Best/Worst scenarios and one-lever-at-a-time sensitivity. Two real bugs
      caught and fixed during verification: (1) the balance sheet didn't balance for any
      projected year because "other assets" was grown independently of NAV instead of
      being the balancing plug; (2) the DDM was discounting all 8 years including the 3
      *actual* (already-paid) years as if they were future cash flows.
- [x] `bizplan/financial/reit_excel_renderer.py` — full formula-linked workbook (Cover,
      Summary, Assumptions, Scenarios, Model with Master Check, Output, Sources), reusing
      `xl_helpers.py` and the CHOOSE-switch scenario architecture. Verified end-to-end
      with the `formulas` Python package (a real Excel-formula evaluator, not just
      openpyxl string-writing) — every Master Check row reads OK across all 8 years in
      all 3 scenarios except the Payout Check for actual years 2023-2025, which reads
      ERROR by design (Acorn's own disclosed payout ratios, 78%/40.5%/34.1%, are
      genuinely below the CMA's 80% minimum in those years — a real governance fact, not
      a bug). Two more real bugs caught by this verification pass: (1) `_assum_ref` was
      missing the `Assumptions!` cross-sheet qualifier, so every Model/Output-sheet
      formula meant to read an Assumptions-sheet input was silently reading the wrong
      cell on its own sheet instead; (2) the Property Portfolio's "Opening Fair Value"
      row self-referenced its own prior column instead of the prior period's *closing*
      balance, so Investment Property froze flat after the first projected year.
- [x] `scripts/build_reit_model.py` (renamed from `build_bank_model.py`), `--reit` flag
      (was `--bank`), default instance `acorn_i_reit` (was `family_bank_kenya`).
      `scripts/launch.sh`/`launch.bat`/`launch.ps1` updated to match; smoke-tested
      end-to-end via `./scripts/launch.sh acorn_i_reit`.
- [x] Deleted `bizplan/financial/bank_calculations.py`, `bank_excel_renderer.py`,
      `examples/family_bank_kenya/` (recoverable via git history / the separately-pushed
      `model_family_bank` repo state from the prior session — nothing lost).
- [x] `BLUEPRINT.md`, `BACKLOG.md` rewritten for the REIT domain (this file).
      `README.md`, `CLAUDE.md`, `AGENTS.md` reframed from bank to REIT terms.
      `CHANGELOG.md` appended (not rewritten — it's an explicit running log).

## Phase 2 — Adapt bizplan/report/* (equity-research-report pipeline) to the REIT domain (2026-08-11) — DONE

- [x] Swapped `bank_calculations`/`bank_excel_renderer` imports for `reit_calculations`/
      `reit_excel_renderer` in `sourcing.py` and `pipeline.py`.
- [x] `bizplan/report/data.py` (Stage 1) rewritten: `company_facts()` now reads
      total_assets/investment_property/nav/nav_per_unit/borrowings/units_in_issue instead
      of the bank shape; `financial_health_grade()` now grades LTV/income-producing-%/
      payout buffers (vs. CMA minimums) instead of capital/liquidity/NPL (vs. CBK
      minimums); `to_report_json()`'s `valuation_per_unit` (renamed from
      `valuation_per_share`) reads straight off `reit_calculations.build_valuation()`'s
      already-per-unit NAV/DDM/cap-rate/blended figures — no shares-outstanding division
      needed, unlike the bank version. Verified against real Acorn I-REIT data: the
      financial-health grade correctly comes back **F** overall (LTV and income-producing
      grade A, payout grades F) — a real, honest signal matching the sector report's own
      criticism of Acorn I-REIT's below-CMA-minimum FY2025 payout ratio, not a bug.
- [x] `bizplan/report/validation.py` (Stage 1b) rewritten: Balance Sheet / LTV /
      Income-Producing-% / Payout, matching the Model sheet's actual 4-row Master Check.
      **Caught a real design bug before it shipped**: a naive port would have required
      the Payout check to pass for every year including the 3 actuals, which are
      *intentionally* below the CMA minimum (real disclosed fact) — that would have made
      `validate_model()` permanently return `ok=False` for a legitimately-correct model
      and permanently blocked `sourcing.py`/`pipeline.py`'s hard `RuntimeError` gate.
      Fixed: the Payout check is required only for projected years; Balance Sheet/LTV/
      Income-Producing are required for every year. Verified `ok=True` against real data.
- [x] `bizplan/report/recommendation.py`, `pdf.py` updated: method-value keys `ddm`/
      `residual_income`/`pb_regression` → `nav`/`ddm`/`cap_rate`; chart labels/axes
      ("per share"/"average PAT") → REIT terms ("per unit"/"average Net Profit"); peer
      table `peer_banks` (name/EPS/ROAE/payout/P-B) → `peer_reits` (name/NAV-per-unit/
      trading-price/discount-premium).
- [x] `bizplan/report/price_research.py`'s prompt text ("book value per share",
      "Bank-basis ground truth") updated to "NAV per unit" / generic ground-truth wording.
- [x] Verified the entire **deterministic** half of the pipeline (Stages 1, 1b, 3, 6 —
      everything that doesn't call `claude -p`) end-to-end against real Acorn I-REIT data:
      `data.compute()`/`to_report_json()`, `validation.validate_model()`,
      `recommendation.mechanical_recommendation()`, and `pdf.build_pdf()` (with hand-built
      stand-ins for the LLM-drafted Stage 2/4/5 outputs) all ran cleanly and produced a
      real 4-page PDF with correct cover-page valuation figures and a correct peer table
      (Acorn I-REIT -4.4% / LAPTRUST Imara +14.0% NAV discount/premium, matching the
      sector report exactly).
- [x] `.devops/agents/equity-report/model-sourcing.md` fully rewritten — it previously
      pointed to `.devops/agents/bank-onboarding.md` for essential onboarding guidance
      (data intake, known pitfalls, `research_output.md` discipline), but that file was
      deleted in an earlier session (the Family-Bank-repo-rename pass) and the SOP was
      silently dangling. Now self-contained for the REIT domain, with pitfalls drawn from
      the real Acorn I-REIT sourcing work (units-in-issue reconciliation gaps,
      internally-inconsistent note tables, full-year-headline-vs-interim-detail
      back-solving, Distributable-Income-vs-Net-Profit, I-REIT-vs-D-REIT regulatory
      limits).
- [x] Remaining SOPs updated to REIT language: `price-consensus-research.md`,
      `review-plagiarism-references.md`, `section-investment-thesis.md`,
      `section-market-consensus.md` (field-name fixes); `section-economic-moat.md` and
      `section-valuation-scenarios.md` (full rewrites — REIT moat sources, NAV/DDM/
      cap-rate blend methodology); `section-financial-health.md` (LTV/income-producing/
      payout sub-grades, CMA not CBK); `section-risks-uncertainty.md` (occupancy/cost-of-
      debt examples, NAV/DDM/Cap-Rate spread). `section-bulls-bears.md`,
      `section-recommendation.md`, `coherence-apply-fixes.md` needed no changes — already
      domain-generic.
- [ ] **Not yet exercised**: the actual `claude -p`-driven stages (Stage 0 sourcing,
      Stage 2 price/consensus research, Stage 4 section drafting, Stage 5 review, Stage
      5.5 coherence gate) — verifying these requires a real `claude -p` run (subscription
      usage, several minutes), which wasn't done as part of this adaptation pass. The SOP
      prompt text has been rewritten and the JSON field contracts it references have been
      confirmed to match what `data.py` actually emits, but a live run is the only way to
      confirm the LLM stages produce coherent REIT-domain prose end-to-end. Try
      `REPORT=1 ./scripts/launch.sh acorn_i_reit` or `python
      scripts/generate_equity_report.py acorn_i_reit --output-dir <dir>` next.

## Phase 3 — Not yet done

- [x] Two-tier seed/stabilized occupancy model (2026-09-03) — replaced the single
      portfolio-blended occupancy glide with per-property-tier modeling using real p.11/
      p.12 disclosures (rooms/beds/operations-start per property; a qualitative seed-vs-
      stabilized operational split). Seed tier's own occupancy back-solved
      `[DISCLOSED-DERIVED]` from two disclosed aggregates (portfolio-blended vs.
      stabilized-tier, bed-weighted) for both H1-2024 and H1-2025. Corrected an initial
      wrong assumption that the split would track property age — it doesn't (oldest
      property is "seed", newest is already "stabilized"); a literal regression wasn't
      fittable from what's disclosed (no per-property occupancy series), so this is a
      disclosure-grounded two-point back-solve, not a regression. Implemented in both
      `reit_calculations.py` (Python ground truth) and `reit_excel_renderer.py` (3 new
      live-formula Model-sheet rows), cross-verified matching with the `formulas` package
      across Base/Best/Worst scenarios; also caught and fixed a latent pre-existing gap
      where the Excel formulas (unlike the Python side) never capped occupancy at 100%.
      See `research_output.md`'s 2026-09-03 section.
- [ ] Item-level opex detail for FY2023/FY2024 is currently a proportional allocation
      from the FY2025 base (see `BLUEPRINT.md` "Known simplifications") — would benefit
      from real per-year, per-item figures if Acorn's full FY2023/FY2024 annual reports
      (not just the interim comparatives) are sourced later.
- [ ] Per-property (not just portfolio-aggregate) fair-value roll-forward, if a
      multi-year per-property history is ever sourced (currently only one point-in-time
      snapshot, 30 Jun 2025, is available).
- [ ] A REIT-specific beta (currently a flagged 0.65 placeholder — no reliable
      regression source given Acorn I-REIT's thin/restricted-market trading).
- [x] Sector-specific cap rate / direct-capitalization cross-check research (2026-08-25)
      — no single authoritative "Kenya REIT cap rate" exists, but real disclosed
      segment yields are now sourced and cross-checked against Acorn's own implied
      5.47%: ILAM Fahari's independently-valued retail/office term & reversionary
      yields (Note 11, FY2025 annual report), ALP Industrial's disclosed industrial
      entry yields (8.17%-9.26%), and general Nairobi residential yield ranges
      (Cytonn/Knight Frank 2025, 5.4%-7.4%). See `research_output.md`'s 2026-08-25
      section. No `config.py` value changed — cross-check/citation only.
- [ ] Extend to a second REIT instance (the user's stated intent: "use it to value other
      REITs"). Sourcing status as of 2026-08-25 (`research_output.md`):
      - **LAPTRUST Imara I-REIT** — fully sourced, 3 years of audited actuals (FY2023-25)
        from its own NSE-hosted filings. Ready for a `config.py` build. Correction to the
        note below: it's *two* consecutive loss/NAV-erosion years (FY2024-25), not three
        — FY2023 was profitable. Fully ungeared all 3 years, clean 80.0% payout every
        year (contrast to Acorn's below-minimum 34.1%). Missing: per-property portfolio
        detail (only aggregate figures found).
      - **ILAM Fahari I-REIT** — fully sourced, FY2025 audited (+FY2024 comparative) from
        its own investor-relations site. Ready for a `config.py` build. Zero borrowings,
        80.7% payout (2025). Missing: trading price / NAV discount-premium (delisted from
        NSE Main Market Feb-2024, no market price disclosed — can't extend the
        `PEER_REITS` table with it).
      - **ALP Industrial REIT** — partially sourced: USD-denominated, maiden H1 2026
        interim only (listed 11-Mar-2026, no full-year annual report exists yet).
        Property-level detail with entry yields (8.17%-9.26%) is disclosed; no
        distributions have been paid yet (CMA 4-month rule). Revisit once a full-year
        report exists.
      - **TRIFIC Green USD I-REIT** — not sourceable yet. Listed 23/29-Jun-2026 (~2
        months before this research pass); no annual/interim report published. Only
        prospectus/guideline forward *projections* found (FY2027 estimates), correctly
        not treated as disclosed actuals. Revisit ~Q1-Q2 2027 once its first annual
        report is likely filed.
      Each still needs a real `config.py` built before it's a usable model instance —
      LAPTRUST Imara and ILAM Fahari are now data-ready for that; ALP Industrial and
      TRIFIC Green USD are not yet.
