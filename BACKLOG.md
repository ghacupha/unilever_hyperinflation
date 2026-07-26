# BACKLOG — Bank Financial Model Generator

Tracks status against `BLUEPRINT.md`. Check items off as they land; append the
corresponding entry to `CHANGELOG.md` when you do. This is the "what's next" doc — read it
before starting work, update it before stopping.

---

## Phase -1 — Repo artifacts & tracking

- [x] `BLUEPRINT.md` written
- [x] `BACKLOG.md` written (this file)
- [x] `CHANGELOG.md` seeded
- [x] Root `CLAUDE.md` updated with tracking instructions

## Phase -0.5 — Environment & primary data source

- [x] `pip install pypdf pdfplumber` into repo-root `.venv` (also `pikepdf` and `pymupdf`,
      needed once the first two hit malformed PDFs — see below)
- [x] Confirm text/table extraction works on at least one `data/` annual report PDF
- [x] **Data quality finding**: 4 of 8 `data/` PDFs are broken.
      `Integrated-Report-and-Financial-Statements-2024.pdf` is genuinely truncated on disk
      (589KB of a declared 27.2MB). `-2025.pdf`, `Integrated-Report-Financial-Statements-
      2021-1.pdf`, and `Family-Bank_MTN-_Information-Memorandum.pdf` have correct total
      byte counts but their PDF Catalog is missing `/Pages` even after `pikepdf` recovery
      (consistent with partial exports from a page-flip/streaming viewer).
      `Integrated-Report-Financial-Statements-2022.pdf` fails even harder (no recoverable
      trailer). **Needs the user to re-download/re-export clean copies.** Full detail in
      `examples/family_bank_kenya/research_output.md`.
- [x] Extract from `data/Integrated-Report-and-Financial-Statements-2023.pdf` (usable,
      204pg): real IFRS 9 stage table by product (Term loans/Mortgage/Overdraft & credit
      cards, not customer segment as originally assumed — config segmentation should
      follow actual disclosure), capital adequacy note, FY2023 actuals. See
      `research_output.md`.
- [x] Extract from `data/ke-fmly-2026-ps-00.pdf` (MTN Information Memorandum 2026, usable,
      276pg): capital adequacy detail, peer bank comparables table (EPS/ROAE/payout/DPS
      for 9 Kenyan banks), sector NIM/NPL/macro outlook. See `research_output.md`.
- [ ] Extract from `data/FBL_LISTING_ABRIDGED_NEWSPAPER_FINAL-1.pdf` (16pg, usable but
      thin) — CAR/liquidity/NPL mentions on p.14-15, not yet pulled in detail
- [ ] Re-extract full IFRS 9 stage tables, capital adequacy 5-yr trend, and segment detail
      once the 4 broken PDFs are replaced with clean copies
- [ ] Pull exact current CBK capital/liquidity minimums from the CBK Prudential Guidelines
      PDF directly (lower priority now — Family Bank's own disclosures already confirm
      10.5%/8%/14.5%/20% and the Shs 5bn 2026 threshold)
- [x] Kenyan government bond yield: 12.32% (10-year, 2 July 2026, Trading Economics) —
      secondary source, usable as CAPM risk-free rate
- [x] Pull exact Kenya figure from Damodaran's country risk premium dataset — total ERP
      13.94% (Jan 2026 data update), see `research_output.md` 2026-07-26 entry
- [x] Research beta for Family Bank / peer average — 0.55, average of 6 NSE-listed peer
      bank betas (Family Bank itself too newly listed for its own beta)
- [x] Peer bank EPS/ROAE/payout/DPS pulled from MTN memorandum (9 banks: Absa, Co-op, DTB,
      Equity Group, I&M, KCB, NCBA, Stanbic, StanChart) — see `research_output.md`
- [x] Peer market cap / book value of equity — resolved via current NSE price / book value
      per share for all 9 peers, see `research_output.md` 2026-07-26 entry
- [x] Forward-looking Kenya macro/sector outlook pulled from MTN memorandum: sector NPL
      peaked 17.6% mid-2025 and moderating, NIM compression expected 2026, Risk-Based
      Credit Pricing Model full rollout by 28 Feb 2026 — see `research_output.md`

## Phase 0 — Modeleon spike (decision gate) — DONE, decided against Modeleon

- [x] Install `modeleon` in scratchpad venv
- [x] Build throwaway loan-book `mo.recurrence()` + cross-sheet ref + scenario switch
- [x] Export to `.xlsx`, confirm live formulas and check formatting control
- [x] **Decision: fall back to `xl_helpers.py`.** Formulas/recurrence/cross-sheet refs work
      genuinely well (`=B1 * (1 + Assumptions!B1)` style live formulas confirmed via
      openpyxl inspection). But `modeleon/compile/excel/writer.py:253-259` only wires
      `number_format` to the Excel writer — `bold`/`bg`/`font_color` passed to
      `Variable.set_style()` are silently dropped, never reach the cell. The layout engine
      is also rigid (one row per Variable, label always col A, data always col B+), which
      doesn't fit the FMI vertical convention (spacer/units columns, indentation, section
      header bars). Not worth fighting for a v0.1.3 library when `xl_helpers.py` already
      gives full control. Proceed straight to Phase 1.

## Phase 1 — Shared formula-capable renderer primitives — DONE

- [x] Create `bizplan/financial/xl_helpers.py`
- [x] Port `fill`/`font`/`align`/`write`/`num`/`pct`/`header_row`/`section_header`/
      `year_header_row`/`data_row`/`total_row`/`blank_row` from `scripts/xl_helpers.py`
      (self-contained — palette inlined rather than importing `scripts/styles.py`, so the
      `bizplan` package doesn't reach outside itself)
- [x] Port formula helpers `_cell`/`_sum_f`/`_add_rows_f`/`_sub_f`/`_ratio_f`/`_ref_f`/
      `_model_ref` — smoke-tested, confirmed formula strings render correctly
- [x] Added `ORANGE` as the fourth "modeled proxy, not disclosed" colour (BLUE_INPUT/DARK/
      TEAL/ORANGE = disclosed input / formula / cross-sheet ref / modeled proxy)

## Phase 2 — Bank calculation layer (`bizplan/financial/bank_calculations.py`) — DONE, verified

- [x] Schedule 1: Loan Book / Staging Schedule (per segment: Term Loans/Mortgage/Overdraft
      & Credit Cards, matching actual disclosure granularity; simplified transition
      mechanic — SICR/default/cure rates applied to opening stage balances, new
      originations sized to hit the target growth rate net of write-offs)
- [x] Schedule 1b: IFRS 9 ECL / Provisioning Schedule — stock-based (loss-rate x closing
      balance, calibrated from real disclosed FY2023 stage coverage ratios) rather than a
      textbook rolling-allowance-with-write-off-utilization approach; P&L charge = period
      -over-period change in the ECL stock (documented in the module docstring — this is a
      deliberate simplification, not a bug, and avoids double-counting write-offs since
      they're already embedded in the closing stock)
- [x] Schedule 2: Investment Securities Schedule
- [x] Schedule 3: Deposit/Funding Schedule (4 types, allocation modeled — only the
      aggregate deposit total is disclosed)
- [x] Schedule 4-5: Interest Income & Interest Expense
- [x] Schedule 6: Net Interest Income & NIM
- [x] Schedule 7: Non-Interest Income (modeled as a ratio of deposits — driver not
      disclosed at this granularity)
- [x] Schedule 8: Operating Expenses
- [x] Schedule 10: Income Statement
- [x] Schedule 11: Cash Flow Statement (indirect) — integrated with the balance sheet so
      cash is the derived plug (standard 3-statement-model mechanic)
- [x] Schedule 12: Balance Sheet — **ties out exactly (check = 0.0 all 5 years)** after
      fixing the opening Other-Liabilities line to be a balancing plug rather than a ratio
      assumption (see commit/changelog — this was a real bug caught by the check itself)
- [x] Schedule 13: Capital Adequacy
- [x] Schedule 14: Liquidity
- [x] Schedule 15: Ratio Disclosures (CAMELS-complete, DuPont ROA decomposition)
- [x] Schedule 16: Valuation (CAPM, DDM, Residual Income, P/B-ROE regression via plain-
      Python least squares — no numpy dependency added for one regression). P/E peer
      cross-check deferred — we have peer EPS/ROAE but not peer share price/book value, so
      there's no real P/E to compute yet (see Phase 4 outstanding items)
- [ ] Best/Worst scenario static comparison values (Scenarios sheet only) — not yet built;
      belongs with the renderer (Phase 3), which is what actually needs a Scenarios sheet

**Verification (Task/BACKLOG item, see Phase 5 for the fuller pass)**: ran `build_all()`
against the Family Bank Kenya config. Balance sheet ties exactly. Plausibility spot-check
vs. real FY2025 disclosed actuals: net loans 105,488.9 modeled vs. 105,900 real (0.4% off);
total capital ratio 19.35% modeled vs. 19.6% real (0.25pp off); deposits 135,231.9 modeled
vs. 151,880 real (~11% low — deposit growth assumption is conservative); NII 12,644.5
modeled vs. 15,630 real (~19% low — yield/cost-of-funds assumptions need a tuning pass).
Loan book and capital adequacy calibrate very tightly; deposits/NII are a good first pass
but flagged for refinement.

## Part A — Repo restructure (moved bank-model code out of `colossal-visuals/`) — DONE

- [x] `colossal-visuals/` confirmed as a standalone reference example (own nested `.git`)
      — not part of this repo's real deliverable; left untouched.
- [x] Moved `bizplan/financial/{xl_helpers,bank_calculations}.py` and
      `examples/family_bank_kenya/{config.py,research_output.md}` to the repo root
      (relocated, not duplicated — confirmed nothing else depended on the old location).
- [x] Uninstalled the stale colossal-visuals editable `bizplan` registration from the
      shared root `.venv` (`pip uninstall bizplan`) — no naming ambiguity now.
- [x] `scripts/build_bank_model.py` — entry point, `sys.path.insert` pattern (no
      pip-install/packaging ceremony needed for our own in-repo code).
- [x] Verified the move: re-ran `build_all()` from the new location, identical output to
      the pre-move verification (balance sheet ties, same plausibility-check numbers).

## Phase 3 — Bank renderer (`bizplan/financial/bank_excel_renderer.py`) — IN PROGRESS

- [x] Assumptions sheet: four-color data-provenance legend, all `config.py` inputs
      (~103 tracked cells), P/B-ROE regression via native Excel `SLOPE()`/`INTERCEPT()`
      referencing the peer table (no hardcoded regression coefficients)
- [x] Model sheet — Loan Book & IFRS 9 Provisioning: per-segment Stage 1/2/3 recurrence
      formulas, ECL, provision charge, aggregate NPL block. Hand-verified: `term gross s1`
      col H traced to 67,333.23 by hand, matches both the Excel formula and
      `bank_calculations.py`'s Python logic exactly.
- [x] Model sheet — Securities/Deposits/Interest Income & Expense/NII
- [x] Model sheet — Non-Interest Income/Opex/Income Statement (PBT→tax→PAT→dividends)
- [x] Model sheet — Cash Flow & Balance Sheet. **Caught and fixed a real bug during
      verification**: the Other-Liabilities opening-plug formula used gross loans instead
      of net loans (in both the renderer and the first draft of the verification script
      itself, which is why they initially agreed on a wrong number) — cross-checked OCF
      year 1 and year 2 against `bank_calculations.py`'s ground truth (exact match after
      the fix) and total assets year 1 (exact match). Balance sheet check row formula in
      place (`Assets − Liab − Equity`), not yet wired to the top-of-sheet Master Check
      section (needs a second pass once all sections are built, since Master Check
      references rows that don't exist yet when the sheet starts).
- [x] Model sheet — Capital Adequacy & Liquidity: RWA (loan book + off-balance-sheet +
      other-assets plug), Tier 1/2, core/total capital ratios, liquidity ratio. Cross
      -checked RWA year 1 (108,554.97, exact match) and ratios against ground truth.
- [x] Master Check section — reserved rows 4-7 at the top of the Model sheet, filled in
      last (`_build_master_check`) once all referenced rows exist. Green/red conditional
      formatting via `FormulaRule` on the OK/ERROR text.
- [x] `bank_calculations.build_scenario()`/`build_scenarios()` — Best/Worst flex loan
      growth/IFRS 9 loss rates/opex escalation via a `_ScenarioConfig` wrapper (shallow
      override of `LOAN_SEGMENTS`/`OPEX_ITEMS`, delegates everything else to the real
      config). Verified: balance sheet ties for all three scenarios; Best/Worst PAT
      trajectories move the sensible direction (Best 4071→5558, Worst 3632→1728).
- [x] Summary sheet: Base/Best/Worst KPI blocks + CAMELS-complete Ratio Disclosures block
      (live `'Model'!`-linked, not static)
- [x] Scenarios sheet: Best/Worst static comparison values
- [x] Valuation sheet: CAPM cost of equity, DDM (live-linked to Model dividends), Residual
      Income cross-check, P/B-ROE regression (native Excel `SLOPE()`/`INTERCEPT()`), all
      three implied values summarized side by side
- [x] Cover sheet
- [x] `build_excel()` orchestrator — sheet tab order fixed to Cover/Summary/Assumptions/
      Scenarios/Model/Valuation via explicit `index=` on each `create_sheet()` call
      (creation order differs from tab order since Model/Assumptions must be populated
      before Summary/Scenarios/Valuation can reference them)

**Verification**: ran `scripts/build_bank_model.py` end to end.
- Sheet order confirmed: `['Cover', 'Summary', 'Assumptions', 'Scenarios', 'Model', 'Valuation']`
- Model sheet: **455 formulas, 0 bare numeric values** in the 5 year data columns — every
  calculated cell is a live formula, the core requirement of this whole project
- Assumptions sheet: 107 hardcoded inputs + 4 derived formulas (macro blend, cost of
  equity, regression slope/intercept)
- Hand-traced and cross-checked against `bank_calculations.py`'s Python ground truth:
  loan staging formula (67,333.23, exact), OCF year 1 and year 2 (exact match after fixing
  a real bug — gross vs. net loans in the Other-Liabilities opening plug), total assets
  year 1 (exact), RWA year 1 (108,554.97, exact)
- **Known limitation**: no LibreOffice/`soffice` on this machine to auto-recalculate and
  literally confirm the Master Check shows "OK" — that final confirmation needs the user
  to open the workbook in real Excel and let it recalculate.

## Phase 4 — Config & research output — DONE (pulled forward during Phase 2)

- [x] `examples/family_bank_kenya/config.py`
- [x] `examples/family_bank_kenya/research_output.md` with `source`/`accessed` fields per item
- [x] `bizplan/config_loader.py`: bank-specific required-fields list / `validate_bank_config()`

## Phase 5 — Entry point, launchers & verification

- [x] `scripts/build_bank_model.py`
- [x] `scripts/launch.sh` (Unix/macOS/Linux) and `scripts/launch.bat` (Windows) — only
      these two, no PowerShell variant. Each: creates `.venv` at the repo root if missing,
      activates it, installs `scripts/requirements.txt`, runs `build_bank_model.py`.
      `launch.sh` tested directly (venv already existed, so it activated and built
      successfully); `launch.bat` written to the same pattern but not tested on this
      machine (no Windows available).
- [x] `scripts/requirements.txt` (`openpyxl>=3.1.0` — the only runtime dependency the
      build itself needs; `pypdf`/`pdfplumber`/`pikepdf`/`pymupdf` were one-off research
      tools, not part of the reusable build path)
- [x] Verify: calculated cells show live formulas, not values — 455 formulas, 0 bare
      numeric values in the Model sheet's data columns
- [x] Verify: Master Check section formulas are in place (BS/CAR/Liquidity, OK/ERROR with
      conditional formatting) — literal "OK" confirmation still needs the user to open the
      workbook in real Excel (no LibreOffice on this machine to auto-recalculate)
- [x] Verify: Year 1/2 Base Case figures plausible vs. `data/`-derived research (see Phase
      2 verification note)
- [x] Verify: Best/Worst scenario columns render (Scenarios sheet, static values)
- [x] Verify: Valuation sheet's three methods produce plausible values, trace live to
      Model sheet (checked formula structure — DDM references `'Model'!` dividends, RI
      references `'Model'!` equity, P/B regression references `Assumptions!` slope/intercept)

## Phase 6 — Structural review vs. FMI reference + CHOOSE-switch rework (2026-07-06) — DONE

- [x] Cell-by-cell structural comparison against `colossal-visuals/references/Blu
      Containers Model - Vertical Complete.xlsx` — see BLUEPRINT.md's "2026-07-06
      structural review" section for full findings
- [x] Extracted real FY2025 Family Bank data (full balance sheet, income statement, IFRS 9
      stage table) now that `data/family_bank/`'s previously-broken PDFs are fixed
- [x] Extracted real peer data where extractable: NCBA P/B 1.2x (disclosed), I&M P/B
      ~0.64x (disclosed-derived from BVPS/price); Absa/Co-op/DTB/Equity/KCB/SCB/Stanbic
      remain `[PLACEHOLDER]` (not found as extractable text in their FY2025 reports)
- [x] `config.py` restructured: YEARS=[2026-2030], opening basis moved FY2023→FY2025,
      `SCENARIO_MULTIPLIERS` added as the single source both Python and Excel scenarios
      read from
- [x] `bank_calculations.build_scenarios()` reads multipliers from config (no more
      hardcoded literals) — verified balance sheet ties for Base/Best/Worst on the new basis
- [x] Renderer: `SWITCH_CELL_REF` + `_scenario_row()` helper — every scenario-dependent
      assumption now renders as Base/Best/Worst/ACTIVE (CHOOSE) rows; Model-sheet formulas
      automatically follow the ACTIVE row since they already looked up cells via the `A`
      dict. "CURRENTLY RUNNING: X SCENARIO" banner added (Model sheet row 1). Scenario
      switch cell lives at `Scenarios!$D$5`.
- [x] Verified: full rebuild succeeds, Model sheet still 456 formulas / 0 bare values,
      hand-traced Term Loans Stage 1 Year 1 formula (84,508.37) against Python ground
      truth on the new FY2025 basis — exact match.

## Phase 7 — Timestamped output folder convention (2026-07-06) — DONE

- [x] `scripts/build_bank_model.py` reads `OUTPUT_DIR` env var (falls back to
      `examples/family_bank_kenya/` when run standalone without a launcher)
- [x] `scripts/launch.sh` / `scripts/launch.bat` create `output/<timestamp>/`, export
      `OUTPUT_DIR`, run the build, then copy `config.py` into that folder (Windows
      timestamp via a `powershell -Command "Get-Date -Format ..."` one-liner — native
      batch date/time parsing is locale-fragile)
- [x] Removed the stale direct-write artifacts (`examples/family_bank_kenya/
      Family_Bank_Kenya_Financial_Model.xlsx`, its Excel lock file, `__pycache__/`) that
      predated this convention
- [x] Verified: `./scripts/launch.sh` creates a fresh `output/<timestamp>/` folder each run
      (not overwriting), with both the `.xlsx` and a `config.py` copy inside; confirmed
      `output/` is already covered by the root `.gitignore`; confirmed running
      `build_bank_model.py` directly (no launcher) still falls back to the old
      direct-write location correctly
- [x] `BLUEPRINT.md` "Project structure" section updated with the convention

## Phase 8 — Historical actuals (2023-2025) + Financial Statement Quality Analysis (2026-07-06) — DONE

- [x] Extracted real disclosed FY2023 full balance sheet/income statement (from FY2024
      report's comparative columns) and real disclosed Cash Flow Statements for
      FY2023/FY2024/FY2025; recorded in `research_output.md`
- [x] `config.py`: added `ACTUALS` dict (2023/2024/2025, per-year real disclosed figures:
      loan segments by stage, off-balance sheet, cash & balances, securities, other
      assets, PP&E, total assets, deposits, other liabilities, total liabilities, share
      capital, retained earnings, total equity, interest income/expense, non-interest
      income, opex, provisions, PBT/tax/PAT, OCF/ICF/FCF, ending cash) and
      `ACTUAL_YEARS = [2023, 2024, 2025]`; all 3 years reconcile exactly
      (Assets − Liabilities − Equity = 0)
- [x] `bank_excel_renderer.py`: reworked every Model-sheet schedule (Loan Book/IFRS 9,
      Securities/Deposits/Interest/NII, Income Statement, Cash Flow/Balance Sheet, Capital
      Adequacy/Liquidity) to show `ACTUAL_COLS` (H,I,J: 2023-2025 — hardcoded real facts +
      same-column subtotal formulas) immediately followed by `DATA_COLS` (K-O: 2026-2030 —
      fully live recurrence formulas), matching Blu Containers' own layout. Simplified
      `_prev()` so the first projected period references the last actual column directly
      (no more Assumptions-sheet opening-scalar fallback needed). Extended Ratio
      Disclosures (Summary sheet) and the Master Check to span all 8 years.
- [x] Scenarios sheet unchanged in scope — actuals are historical fact, not
      scenario-dependent, so only the 5 projected columns vary by Base/Best/Worst
- [x] New "Financial Statement Quality Analysis (Actuals only)" section on the Valuation
      sheet: Sloan (1996) Accruals Ratio, PAT-vs-OCF trend with a decline flag, Texas
      Ratio (bank distress indicator), and an explicitly-labeled adapted Beneish M-Score
      proxy (bank-equivalent substitutions per component, DEPI omitted for lack of
      actual-year D&A detail, prominent caveat that the original -2.22 threshold doesn't
      apply) — computed only over the 3 actual years, not the projection
- [x] Fixed a Balance Sheet reconciliation bug caught during verification: the actual-year
      Total Assets formula was using the Cash Flow Statement's own "cash and cash
      equivalents" figure (a narrower disclosure than the Balance Sheet's own "cash and
      balances with CBK + due from banks") — switched to the correct BS-definition figure
      for the Total Assets build-up; Balance Sheet Check now ties to 0.0 for all 3 actual
      years (previously off by exactly the inter-bank-balances amount each year)
- [x] Verified: Balance Sheet Check ties for all 3 actual years and all 5 projected years
      (Base/Best/Worst, via direct `bank_calculations.py` recompute); hand-traced the
      Texas Ratio and the 2024 Beneish M-Score proxy against independent Python ground
      truth (exact match); confirmed Scenarios sheet still shows projected-only columns

## Phase 9 — CLI wiring, regulatory capital bridge, sector concentration (2026-07-06) — DONE

- [x] `scripts/build_bank_model.py`: `--bank NAME` (default `family_bank_kenya`, resolves
      to `examples/NAME/config.py`) and `--config PATH` (explicit override) via `argparse`.
      `scripts/launch.sh`/`launch.bat` accept an optional first positional bank-name arg,
      pass it through, and resolve the post-build `config.py` copy dynamically.
- [x] `bizplan/config_loader.py`: `REQUIRED_FIELDS` now includes `ACTUALS`,
      `ACTUAL_YEARS`, `REGULATORY_CAPITAL` (the first two were genuinely required by the
      renderer since Phase 8 but the validator wasn't updated — now fails fast on a
      malformed config instead of a deep `KeyError`).
- [x] **Regulatory capital bridge**: discovered `CAPITAL['opening_tier1']` was total
      accounting equity, not real regulatory Tier 1 (24,404.354 for FY2025 per Family
      Bank's own Capital Management note) — exactly why the modeled CAR didn't reconcile
      to the disclosed 16.9%/19.6%. Added `config.py`'s `REGULATORY_CAPITAL` (real
      Tier 1/Tier 2/RWA build-up, 2023-2025, using the FY2025-report-restated FY2024
      figures per the project's established restatement convention). Reworked
      `_build_capital_liquidity_section` (`bank_excel_renderer.py`) to show the real
      build-up (Share Capital/Premium/Retained Earnings/Less Deferred Tax → Tier 1;
      Revaluation/Sub Debt/Statutory Reserve → Tier 2) as hardcoded facts for actual
      years, and real disclosed RWA (no Basel credit/market/operational split exists in
      Family Bank's own filings to build a finer projected model against). Projected
      years use new calibrated drivers anchored to the real FY2025 point:
      `tier1_pct_of_equity` (0.7481), `reg_tier2_opening` (3,899.296, held flat), and
      `other_rwa_pct_of_gross_loans` (0.3347, replacing a flat plug so RWA scales with the
      book). `bank_calculations.py`'s `build_capital_adequacy` mirrors the same drivers for
      the Scenarios sheet's Python ground truth. Balance Sheet mechanics (accounting
      equity roll-forward, Other Liabilities plug) are untouched — the regulatory figures
      are a parallel calculation, not derived from or feeding into the accounting Balance
      Sheet (confirmed: real Tier 2 includes statutory/revaluation reserve, which sit
      within accounting equity, not liabilities — the two concepts genuinely diverge).
- [x] **Sector concentration**: no CBK single-borrower/large-exposure limit or Family
      Bank's own largest exposures are disclosed anywhere (confirmed via targeted search)
      — per user decision, skipped rather than fabricate a check against a number that
      doesn't exist in the disclosure. Added a new "Loan Book Concentration — Sector
      Detail" schedule (actuals only) instead: real disclosed loan-by-sector tables for
      FY2024/FY2025 (10-category scheme) plus a separate FY2023 footnote table (prior
      7-category scheme, not directly comparable) — both with live Total/％-of-Total
      formula rows.
- [x] Verified: actual-year Core Capital/RWA and Total Capital/RWA tie exactly to
      13.47%/18.89% (2023), 13.52%/17.76% (2024, restated), 16.87%/19.56% (2025);
      Balance Sheet Check still ties for all 8 years/all scenarios (unaffected); projected
      -year CAR ratios continue smoothly from the FY2025 anchor (17.4%→18.1%, Base case);
      sector table totals match disclosed totals exactly; CLI flags tested (`--bank`,
      `--config`, invalid-bank error path, both launchers).

## Phase 10 — Bank-only data, full Balance Sheet line-item detail, scroll-safe headers (2026-07-06) — DONE

- [x] **Bank (standalone) vs Consolidated (Group) data correction**: discovered every
      actual figure was sourced from the Consolidated column of Family Bank's annual
      reports, not the Bank column (both are disclosed side-by-side for every statement,
      every year). Per the modeling principle that a bank in a group should be modeled
      on its own bank data, re-sourced every actual figure — Balance Sheet, Income
      Statement, Cash Flow — to the Bank column for all 3 actual years (see
      `research_output.md`'s "Update 2026-07-06 (later still)" for the full
      reconciliation, including two real cash-equivalents-definition restatement quirks).
      Cascading corrections applied to `DEPOSIT_TYPES`, `INVESTMENT_SECURITIES`, `PPE`,
      `CAPITAL['opening_tier1']`, `OPEX_ITEMS`, `NON_INTEREST_INCOME_RATE` (all
      numerically derived from the FY2025 Bank figures, per `config.py`'s docstring
      convention) — `bank_calculations.py` needed no code changes, only correct data
      flowing through its existing formulas.
- [x] **Full Balance Sheet line-item detail**: the Model sheet's Balance Sheet block
      previously showed a single "TOTAL ASSETS" row and 3 liability/equity aggregates —
      now shows all ~28 real disclosed line items (Cash & CBK, Due from/to Banks,
      Government Securities split by classification, Investment in Subsidiaries,
      Investment Properties, Intangibles, ROU Assets, Prepaid Leases, Tax Assets/
      Liabilities, Accruals & Provisions, Borrowings, Lease Liabilities, and the full
      equity reserve breakdown: Share Capital, Share Premium, Revaluation Surplus, Fair
      Value Reserve, Statutory Reserve, Proposed Dividends, Retained Earnings) as
      hardcoded facts for actual years. Projected years reuse existing drivers where one
      exists (Cash Flow roll-forward, `INVESTMENT_SECURITIES` growth, the Loan Book
      schedule, PP&E roll-forward — split into sub-lines via the FY2025 actual mix) or
      grow independently at a new generic `OTHER_BS_ITEMS_GROWTH_RATE` where none is
      disclosed. Retained Earnings becomes a residual/plug for projected years,
      preserving the exact pre-existing Total Equity roll-forward mechanic by
      construction (verified algebraically and numerically) so the Balance Sheet Check
      couldn't regress.
- [x] **Scroll-safe period headers**: added `MASTER_HEADER_ROW` + `_linked_year_header_row()`
      — every Model-sheet schedule now repeats a formula-linked copy of the sheet's
      single master year-header row (not a duplicated literal), so scrolling anywhere on
      the ~250-row Model sheet never loses the column-to-period mapping. Master header
      relabeled "2023A"..."2025A"/"2026P"..."2030P" (suffix helper `_period_label()`);
      applied to every sheet with year columns (Model, Summary, Scenarios, Valuation).
- [x] Verified: all 3 actual years' granular Balance Sheet rows sum to the real disclosed
      Total Assets/Liabilities/Equity exactly (independent Python check); Balance Sheet
      Check ties for all 8 years and all 3 scenarios (`bank_calculations.py`, unaffected
      by the renderer rework); hand-traced the full Excel formula chain for FY2023-2025
      and the first projected year; confirmed header-linking formulas and period-suffix
      labels render correctly across all 4 sheets.

## Phase 11 — Per-share equity valuation (2026-07-06) — DONE

- [x] Also fixed a real bug found by inspection: the CAPM cost-of-equity rows on the
      Valuation sheet (Risk-free rate/Beta/ERP/Cost of equity) were missing the leading
      `=` on their cross-sheet reference formulas, so Excel stored them as literal text
      (e.g. `Assumptions!$H$206`) instead of live formulas — cascaded into a `#VALUE!`
      error on Terminal Value and the whole Residual Income model. Fixed all 4 cells.
- [x] Added `SHARES_OUTSTANDING_2025` (1,662.655m, `[DISCLOSED]`, FY2025 report's share
      capital note p.265 — confirmed KES 1.00 par value, so the share-capital account
      balance in KES millions already *is* the share count for any year). Added
      "Implied Value Per Share (KES)" under each of the DDM/Residual Income/P-B-ROE
      Regression implied equity values, and extended the Summary comparison table with a
      Per Share column alongside the existing Total (KES MM) column.
- [x] Added a "Book Value Per Share (Actuals)" cross-check row (2023-2025), each year
      using its own share count (`ACTUALS[y]['share_capital']`, already in `config.py` —
      share count changed year to year via the FY2023 rights issue and FY2025 private
      placement, so the FY2025 count can't be applied retroactively). Verified against
      Family Bank's own disclosed Consolidated-basis BVPS (17.15→19.62): our Bank-basis
      figures come in slightly lower (16.64/19.31), the expected gap given this model's
      bank-not-group basis, not a discrepancy.
- [x] Verified: per-share figures equal aggregate implied equity value ÷ 1,662.655
      exactly; BVPS actuals reproduce the expected small gap vs the disclosed Group-basis
      figures; Summary table renders both columns correctly.

## Phase 12 — Repo cleanup (root duplicates) (2026-07-14) — DONE

- [x] Deleted root-level `bank_calculations.py`, `bank_excel_renderer.py`, `xl_helpers.py`,
      `config_loader.py`, `config.py`, `build_bank_model.py`, `__init__.py`, the root
      `financial/` directory, and root `launch.bat`/`launch.sh` — all confirmed
      byte-identical duplicates of `bizplan/`/`scripts/` files, never imported by anything
      on the live launch path (`scripts/build_bank_model.py` → `bizplan.config_loader` →
      `bizplan.financial.*`).
- [x] Verified: rebuilt via `scripts/build_bank_model.py` directly from a clean tree —
      identical output to before the cleanup.

## Phase 13 — Print/page setup (2026-07-14) — DONE

- [x] `_apply_print_setup()` helper (`bank_excel_renderer.py`): landscape orientation,
      scale=95, horizontally-centered, matching the Blu Containers reference convention.
      Single-block print area on Cover/Summary/Assumptions/Scenarios/Output; multi-block
      (one per schedule section: Loan Book, Funding, Income Statement, Cash Flow/Balance
      Sheet, Capital/Liquidity) on Model, computed from the existing section-builder
      return-row chain — no changes needed inside the section builders themselves.
      `print_title_rows = "1:1"` on every non-Cover sheet so the banner (Phase 14) repeats
      on every physically printed page.

## Phase 14 — Top-right scenario banner (2026-07-14) — DONE

- [x] `_scenario_banner_formula()` — a `HYPERLINK()` formula to `Scenarios!D5` wrapped
      around the existing `CHOOSE()`-driven "Base/Best/Worst CASE" text. Placed at row 1,
      rightmost content column, on Assumptions/Scenarios/Model/Summary/Output — retired the
      old Model-sheet-only banner at column H in favor of one consistent cell per sheet.

## Phase 15 — Rename "Valuation" sheet to "Output" (2026-07-14) — DONE

- [x] `build_valuation_sheet` → `build_output_sheet`; sheet tab "Valuation" → "Output";
      updated module docstring, Cover sheet's tab bullet list, and `BLUEPRINT.md`'s 6
      occurrences. Confirmed zero `'Valuation'!` cross-sheet formula references existed
      anywhere (pure leaf/consumer sheet) — the rename was fully self-contained. Left the
      in-sheet "Equity Valuation — Base Case" heading as-is (names the methodology, not
      the tab).

## Phase 16 — Scenario metric block redesign (2026-07-14) — DONE

- [x] Reworked `_scenario_row()` (Assumptions sheet) and added `_scenario_metric_block()`
      (Scenarios sheet, replacing the old case-grouped Base/Best/Worst layout) to a shared
      compact-table convention per the user's mock-ups: a title bar carrying the metric
      name/unit once, a boxed `CHOOSE()`-driven ACTIVE row on top, a blank spacer, then
      plain Base/Best/Worst rows below — short labels only, since the title bar already
      carries the metric name/unit. Added `box_border()` to `xl_helpers.py`. Scenarios
      sheet restructured from case-grouped (3 case blocks × 8 metrics each) to
      metric-grouped (8 metric blocks, each showing its own live ACTIVE row above the three
      static Base/Best/Worst comparison rows).
- [x] Verified: `refs[key] = active_row` contract unchanged (downstream `A[key]` lookups on
      the Assumptions sheet unaffected by the row reorder); rebuilt end-to-end, Model sheet
      formula count unaffected.

## Phase 17 — Scenario switch: Data Validation dropdown (2026-07-14) — DONE

- [x] Added an in-cell `DataValidation` list (`"1,2,3"`) on `Scenarios!D5` — user decision:
      ship the simple, robust openpyxl-native option first; a true Excel Forms combo box
      (matching the Blu Containers reference exactly) is an explicit, not-yet-committed
      fallback if the dropdown UX proves insufficient — the necessary raw-OOXML parts were
      reverse-engineered against both the reference and the user's own partial manual
      attempt during planning, so a follow-up phase wouldn't start from scratch.

## Phase 18 — Standalone Python onboarding/update agent (2026-07-14) — DONE

- [x] `agent/` package (`cli.py`, `research.py`, `config_writer.py`, `manifest.py`,
      `build_runner.py`) — a standalone program (not a Claude Code subagent) that calls the
      Anthropic API directly: a manual tool-use loop with the server-side `web_search` tool
      plus a custom `download_file` tool locates and fetches a new institution's filings,
      then the downloaded PDFs are fed back to Claude as native `document` content blocks
      for extraction (falling back to the repo's existing pypdf/pdfplumber/pikepdf/pymupdf
      recovery toolchain only if a PDF fails to parse via the API). Writes
      `examples/<institution>/config.py` (validated immediately against
      `bizplan/config_loader.REQUIRED_FIELDS`) and `research_output.md`, then runs the
      existing renderer unchanged via `scripts/build_bank_model.py --bank <institution>`.
      `update <institution>` re-runs the research step scoped to "anything newer than the
      manifest's last-ingested sources" and, if found, rolls the config forward
      (nearest-projected-year → `ACTUALS`, `YEARS` extended by one) rather than
      regenerating from scratch.
- [x] `.devops/agents/bank-onboarding.md` — the institution-agnostic SOP the agent's
      prompts are grounded in, distilled from this file's own Phase -0.5 through Phase 11
      (including the real pitfalls hit along the way: broken source PDFs, Bank-vs-
      Consolidated column confusion, the two cash-flow-definition mismatches, regulatory
      vs. accounting Tier 1).
- [x] `AGENTS.md` (new, root) indexing both; one-line pointer added to `CLAUDE.md`.
- [x] Verified: all new `agent/*.py` files parse cleanly (`ast.parse`); not yet exercised
      end-to-end against the live Anthropic API in this session (needs `ANTHROPIC_API_KEY`
      + real network access + real API spend — a genuine "run it for real" step left to the
      user).

## Phase 19 — Fix CHOOSE off-by-one on the Scenarios sheet (2026-07-14) — DONE

- [x] **Real bug, found by the user reviewing the rendered output**: `_scenario_metric_block()`
      did two separate `row += 1` calls right after writing the boxed ACTIVE row — one to move
      past it, one meant as "the blank spacer before Base/Best/Worst" — which shifted every
      subsequent row one below where the `CHOOSE()` formula's `base_row`/`best_row`/`worst_row`
      actually pointed. `base_row` was never written to (Excel reads it as 0 → Base always
      showed 0); "Base" data landed where the formula read for Best; "Best" landed where it
      read for Worst; the real "Worst" data was orphaned one row further down, never
      referenced. `_scenario_row()` (the Assumptions-sheet equivalent) never had this bug — it
      only increments once per row with no spacer, which is what confirmed the bug was
      isolated to the Scenarios sheet.
- [x] Fix: exactly one `row += 1` between the active row and Base; the blank spacer moved to
      between the title bar and the active row instead (also applied to `_scenario_row` for
      consistency, per the user's revised visual preference — see Phase 20).
- [x] Verified: wrote a script asserting, for every metric block on the Scenarios sheet, that
      the `CHOOSE()` formula's three cell operands actually hold rows labeled "Base"/"Best"/
      "Worst" respectively — zero mismatches across all 8 metric blocks.

## Phase 20 — Group outline border + tighter columns (2026-07-14) — DONE

- [x] New `outline_range()` in `xl_helpers.py` — draws one bounding rectangle around a
      contiguous horizontal group of cells (left edge only on the first column, right edge
      only on the last, top+bottom on every column) instead of `box_border()`'s every-cell-
      gets-all-four-sides, which read as a grid of separate boxes rather than one outlined
      group. Swapped into both `_scenario_metric_block` and `_scenario_row`.
- [x] `_col_widths()` data columns (H-O) reduced from 14 to 12 (still comfortably fits the
      largest modeled figures). The Scenarios sheet never uses `ACTUAL_COLS` (H-J) at all —
      only `DATA_COLS` (K-O) — so those three full-width unused columns were most of the
      "too much space between columns" effect; narrowed to width 3 on that sheet specifically
      (Assumptions keeps them at full width — Phase 21 puts real data there).

## Phase 21 — Assumptions: Loan Book & Deposits as tables (2026-07-14) — DONE

- [x] Restructured the "LOAN BOOK — BY PRODUCT" and "DEPOSITS / FUNDING" sections from one
      repeated ~12-row vertical block per category (3× for loan segments, 4× for deposit
      types) into one table per section: a header row naming each category once, then one row
      per metric spanning all category columns. Cuts the Loan Book section from 36 rows of
      near-identical labels down to 12 metric rows (+ header); Deposits from ~12 down to 3
      (+ header).
- [x] The real constraint this ran into: every downstream Model-sheet formula reads a
      per-segment assumption via `_assum_ref(A, key)`, which assumed a single global
      `ASSUM_COL` varying only by row. Moving categories into columns meant `_assum_ref`
      needed to know *which* column too. Fixed with a backward-compatible change: `A[key]`
      can now be either a bare row int (existing behavior, ~40 of 57 call sites untouched) or
      a `(row, col)` tuple (new, for table-clustered keys) — `_assum_ref` transparently
      resolves either shape, so none of the ~15-18 call sites in `_build_loan_book_section`/
      `_build_funding_section` that reference segment/deposit-typed keys needed to change at
      all.
- [x] New `_table_row()` (plain per-category metric row) and `_scenario_table_row()` (the
      multi-column generalization of `_scenario_row`: title, spacer, outlined ACTIVE row with
      one `CHOOSE()` per category column, then Base/Best/Worst) in `bank_excel_renderer.py`.
      Column counts derive from `len(config.LOAN_SEGMENTS)`/`len(config.DEPOSIT_TYPES)` rather
      than being hardcoded, so this generalizes to a future institution with a different
      number of loan products or deposit types.
- [x] Verified: rebuilt end-to-end — Model sheet formula count unchanged (636 formulas, 5 
      pre-existing bare placeholder values, unaffected), Balance Sheet Check formula intact,
      and confirmed by inspection that Model-sheet formulas for the Mortgage/Overdraft
      segments now correctly reference `Assumptions!$I$...`/`$J$...` (their own columns)
      rather than all collapsing onto column H.

## Phase 22 — `.env` file for the agent (2026-07-14) — DONE

- [x] `.env` at repo root with `ANTHROPIC_KEY=` (placeholder). Confirmed already covered by
      `.gitignore`.
- [x] `agent/cli.py`: added `_anthropic_client()` — loads `.env` via `python-dotenv` and
      constructs the client explicitly off `ANTHROPIC_KEY`, since the Anthropic SDK's own
      auto-detection only looks for `ANTHROPIC_API_KEY`/`ANTHROPIC_AUTH_TOKEN`, not this
      repo's chosen variable name. Raises a clear error if the key is missing rather than
      failing deep inside the SDK. Added `python-dotenv` to `agent/requirements.txt`.

## Phase 23 — Blended valuation, per-scenario valuation, Net Income sensitivity (2026-07-26) — DONE

- [x] Researched industry/academic practice for combining DDM + Residual Income + relative
      (P/B-ROE) valuation into one number — no universal weighting formula found; adopted
      50% DDM / 30% RI / 20% P/B-ROE, operationalizing this file's own pre-existing method
      hierarchy. Full write-up in BLUEPRINT.md's "2026-07-26" section.
- [x] `bank_calculations.build_valuation()` returns `blended_value`; flows through
      `build_scenarios()` for Base/Best/Worst automatically (no new plumbing needed there).
- [x] Output sheet: new "Blended Valuation" section (live formula) after the existing
      three-method summary table; 3 new configurable weight rows on the Assumptions sheet.
- [x] Summary sheet: new "Implied Value Per Share by Scenario" table (Base/Best/Worst ×
      DDM/RI/P-B-ROE/Blended), static-Python-value convention matching the existing KPI
      blocks.
- [x] `bank_calculations.build_sensitivity()`: one-lever-at-a-time PAT impact. 3 factors
      cross the >10% average-PAT bar: loan/balance-sheet growth (-19.5%/+14.0%), asset
      yield/lending rate (±15.0% per 100bp), cost of funds/deposit pricing (±22.7% per
      100bp). Loss-rate and opex-escalation levers tested and excluded — don't cross 10% at
      their currently configured Best/Worst magnitudes (see BLUEPRINT.md for the honest
      negative finding and its implication for those multipliers' calibration).
- [x] New "Key Net Income Sensitivities" section on the Summary sheet.
- [x] Rebuilt end-to-end; Balance Sheet Check, Capital Adequacy, and Liquidity all still OK
      for every projected year.

## Phase 24 — Equity Research Report pipeline (IN PROGRESS)

Preliminary architecture in `BLUEPRINT.md` (2026-07-26, "Equity Research Report pipeline"
section, once added) — a `claude -p` (subscription-billed, not raw-API-billed) pipeline
generating both the Excel model and a Morningstar-style PDF, generic across institution
AND an "as-of" anchor period (3 actuals ending there, 5 years projected forward).

- [x] Phase A — pure-Python ground truth + validation, no LLM involved:
      `bizplan/financial/bank_validation.py` (`validate_model()` — re-implements the Model
      sheet's 3-check "Master Check" — Balance Sheet, Capital Adequacy, Liquidity — in
      Python, same tolerances) and `bizplan/financial/report_data.py` (`compute()` +
      `to_report_json()` — serializes `build_all()`/`build_scenarios()`/
      `build_sensitivity()` into the JSON every later report-writing stage will read).
      Tested standalone against `family_bank_kenya`: validation `ok=True` for all 5
      projected years; JSON output correct (blended value 14.20/share, 3 sensitivity
      factors, Base/Best/Worst scenario valuation all present).
- [ ] Stage 0 — model sourcing generalized to (institution, as-of year) -> config.py
- [ ] Stage 2 — price/consensus research (`claude -p`, needs a reference-date parameter
      for backtesting validity)
- [ ] Stage 3 — mechanical Buy/Hold/Sell pre-decision (Morningstar-style margin-of-safety
      bands, uncertainty-tier mapping not designed yet)
- [ ] Stage 4/5 — per-section report drafting + plagiarism/references review
- [ ] Stage 6 — PDF assembly (ReportLab + matplotlib), `launch.sh` wiring

## Follow-ups (not blocking)

- [x] Real P/B for Absa/Co-op/DTB/Equity/KCB/SCB/Stanbic — resolved via live web lookup
      (current NSE price / book value per share), not company filings; see
      `research_output.md` 2026-07-26 entry
- [x] Beta — no true regression performed (still no historical price series/index-return
      access), but resolved with a defensible proxy: average of 6 NSE-listed peer banks'
      published equity betas (0.55), replacing the earlier generic 1.0 midpoint
- [ ] True Excel Forms combo box for the scenario switch (fallback to Phase 17's
      DataValidation dropdown, only if the user finds it insufficient — see Phase 17)
- [ ] `agent/` CLI's first live end-to-end run against a second real institution (needs a
      real `ANTHROPIC_KEY` in `.env` + user-provided starting URLs) — proves out the whole
      pipeline the way `scripts/build_bank_model.py` is already proven for Family Bank Kenya
