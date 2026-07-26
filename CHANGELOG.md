# CHANGELOG

All meaningful changes to the bank financial model generator. Each entry should name which
`BLUEPRINT.md` phase / `BACKLOG.md` item(s) it closes.

---

## [Unreleased]

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
