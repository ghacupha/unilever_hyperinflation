# Blueprint: Reusable Bank Financial Model Generator

**Status:** Design approved 2026-07-05; structurally reviewed against the FMI reference
(Blu Containers) and reworked 2026-07-06 — see `BACKLOG.md` for current status and next
steps, `CHANGELOG.md` for what has actually landed.

## 2026-07-06 (later still) — Bank-only data, full Balance Sheet detail, scroll-safe headers

Two problems surfaced from reviewing the rendered workbook directly against Family Bank's
own disclosures (screenshots of the real Balance Sheet, Assets and Liabilities &
Shareholders' Funds sides):

- **Every actual figure had been sourced from the Consolidated (Group) column, not the
  Bank (standalone) column** — both are presented side-by-side in every annual report,
  for every statement. Per the modeling principle that a bank within a group should be
  modeled on its own bank data (not diluted/inflated by subsidiary consolidation), every
  actual figure was re-sourced to the Bank column. This is a genuinely different
  reconciliation problem from the FY2024 restatement quirks found earlier — Bank vs
  Consolidated is two DIFFERENT REAL NUMBERS for the same fiscal year, not a
  report-vintage question. Two of the restatement quirks already documented for
  Consolidated figures turned out to recur on a Bank basis too (Family Bank's "cash and
  cash equivalents" definition broadened twice across report vintages) — same "prefer
  the most recent restatement" convention applied again.
- **The Model sheet's actual Balance Sheet block showed almost nothing** — a single
  "TOTAL ASSETS" row (built from aggregates living elsewhere on the sheet) and 3
  liability/equity lines, when Family Bank discloses ~28 distinct line items. Root cause:
  since Phase 8, `config.py`'s `ACTUALS` had been blending 5-7 real distinct disclosure
  lines into single buckets (e.g. `other_assets` blended 7 items; `retained_earnings`
  blended 5) as a deliberate simplification, which the renderer then surfaced as one row
  each rather than the real itemized statement.

**Fix, and the key design principle for the rework**: where a specific driver already
exists and works (Cash via the CF roll-forward, Securities via `INVESTMENT_SECURITIES`
growth, Loans via the Loan Book schedule, PP&E via its own roll-forward, Retained
Earnings via the PAT-minus-dividends roll-forward the Balance Sheet Check depends on),
keep that mechanic completely unchanged and split it into presentational sub-lines via a
proportional allocation calibrated to the FY2025 actual mix — this preserves every
existing mechanical linkage exactly. Where no driver exists today (the old blended
buckets), build bottom-up from real per-line actual facts, each independently growing at
a new generic `OTHER_BS_ITEMS_GROWTH_RATE` for projected years — strictly additive to a
schedule's total, so there's no Balance Sheet Check risk either way.

The one place needing real care: Retained Earnings' projected-year value becomes a
**residual/plug** — `Total Equity(t) [via the unchanged pre-existing roll-forward] − every
other equity sub-line`. This preserves the exact existing mechanic algebraically (proven,
not just tested): since every other equity line's value cancels out of the plug
computation, `Total Equity(t) = _prev(equity_row) + PAT(t) − Dividends(t)` by
construction, identical to `bank_calculations.py`'s own `tier1[i] = tier1[i-1] + pat[i] -
dividends[i]` recursion (confirmed: the Python engine's Balance Sheet Check still ties
across all scenarios with zero code changes there, only the underlying `CAPITAL
['opening_tier1']` data correction cascading through).

Also fixed (raised in the same conversation): the ~250-row Model sheet only had a year
header at its very top and one other spot, so scrolling anywhere else lost the
column-to-period mapping entirely. `_linked_year_header_row()` repeats a **formula
-linked** copy (not a duplicated literal) of the sheet's single master header row at the
start of every schedule — a single source of truth, changing the master row propagates
everywhere. Columns relabeled "2023A"/"2026P"-style across every sheet with year columns.

## 2026-07-06 (later) — CLI wiring, regulatory capital bridge, sector concentration

Worked through three of `BACKLOG.md`'s non-blocking follow-ups (CLI wiring, deeper CBK
compliance detail, full regulatory-capital bridge); the other two (real peer P/B, a true
regression beta) stayed out of scope — still no data source to unblock them.

- **CLI wiring**: `scripts/build_bank_model.py` takes `--bank NAME`/`--config PATH`;
  both launchers accept an optional bank-name arg. Makes the generator genuinely reusable
  across bank instances without editing code, and closes a real validation gap
  (`config_loader.py` didn't require `ACTUALS`/`ACTUAL_YEARS`, added this session, even
  though the renderer already depended on them).
- **Regulatory capital bridge — a real, previously-undiagnosed bug**: `CAPITAL
  ['opening_tier1']` (32,622.486) turned out to be total accounting equity, not real
  regulatory Tier 1 capital. Family Bank's own Capital Management note discloses the full
  Tier 1/Tier 2/RWA build-up for FY2023-FY2025 — real regulatory Tier 1 for FY2025 is
  24,404.354, an ~8.2bn gap from the accounting-equity figure the model had been using.
  This is exactly why the modeled Core/Total Capital ratios never reconciled to the
  disclosed 16.9%/19.6%, despite the earlier design note's acknowledgment of the gap.
  **Important structural finding**: `opening_tier1`/`opening_tier2` can't simply be
  repointed to the real regulatory figures — they're load-bearing for the Balance Sheet's
  opening retained-earnings derivation and the Other Liabilities plug in
  `bank_calculations.py`. Regulatory capital is a genuinely *parallel* calculation to the
  accounting Balance Sheet (real Tier 2 includes statutory/revaluation reserve, which sit
  within accounting equity, not liabilities — the two classifications diverge by design,
  not by data error). Solution: added `REGULATORY_CAPITAL` (real per-year build-up) plus
  new, clearly separate projected-year drivers (`tier1_pct_of_equity`,
  `reg_tier2_opening`, `other_rwa_pct_of_gross_loans`) calibrated to the real FY2025
  anchor, leaving the Balance Sheet's own accounting-equity mechanics completely
  untouched. No Basel-style credit/market/operational RWA split exists anywhere in Family
  Bank's own filings (confirmed via targeted search) — the model's own Loan Book/
  Off-Balance-Sheet RWA rows remain a useful cross-check but aren't summed into the real
  disclosed RWA total for actual years.
- **Sector concentration, scoped down from "CBK compliance detail"**: targeted search
  confirmed no single-borrower/large-exposure limit or Family Bank's own largest
  exposures are disclosed anywhere — only generic risk-policy narrative. Rather than
  fabricate a compliance check against a number that doesn't exist in the disclosure,
  built a real sector-concentration schedule instead, using Family Bank's actual
  disclosed loan-by-sector tables (noting the 7-category → 10-category scheme change
  between FY2023 and FY2024/2025, shown as two separate tables rather than forced into
  one comparison).

## 2026-07-06 — Historical actuals + Financial Statement Quality Analysis

Revisited the earlier "anchor 2026 to real FY2025 data" decision (above): rather than the
projection's first year merely being calibrated off real data, the Model sheet now carries
genuine actual-year columns, matching Blu Containers' own pattern of 3 historical columns
immediately followed by projected columns on every schedule.

- **3 actual years (2023-2025) + 5 projected years (2026-2030)** on every Model-sheet
  schedule — Loan Book/IFRS 9, Securities/Deposits/Interest/NII, Income Statement, Cash
  Flow/Balance Sheet, Capital Adequacy/Liquidity. `ACTUAL_COLS = [H, I, J]`,
  `DATA_COLS = [K..O]`. Actual-year raw disclosed line items are hardcoded (`BLUE_INPUT`);
  subtotals/derived rows are still live same-column formulas, not static dumps — matching
  how the reference's own historical columns work (e.g. its `J13 =J10-J12`).
- **Mechanical simplification this unlocked**: since real actual columns now exist
  directly on the Model sheet, the projected recurrence's first period (`_prev(i=0, ...)`)
  just references the last actual column, same row, same sheet — removed the old
  Assumptions-sheet "opening scalar" fallback entirely rather than adding a new special
  case for it.
- **Actual years use real hardcoded aggregates, not forward-looking assumption rates
  applied to historical balances** — e.g. Total Interest Income/Expense, Non-Interest
  Income, Total Opex, PBT, Tax are hardcoded straight from disclosed figures for 2023-2025;
  granular sub-splits (per-deposit-type interest expense, per-opex-category detail) are
  left blank where the real disclosure doesn't break them out that finely, rather than
  fabricated from a forward-looking rate.
- **Balance sheet definition-of-cash pitfall** (worth flagging for future model
  instances): a bank's disclosed Cash Flow Statement "cash and cash equivalents" figure
  and its Balance Sheet's own "cash and balances with CBK + due from banks" figure are
  *not* the same number — they differ by inter-bank balances. The CF statement's own
  Ending Cash Balance row must use the CF figure; the Balance Sheet's Total Assets must use
  the BS figure. Conflating them (reusing one hardcoded cell for both) breaks the Balance
  Sheet Check by exactly the inter-bank-balances amount.
- **Financial Statement Quality Analysis** (Valuation sheet, actuals only — the projection
  is our own modeling, not a filing to scrutinize): Sloan (1996) Accruals Ratio
  `(PAT − OCF) / Average Total Assets` (applies to banks unmodified); PAT-vs-OCF trend with
  a decline flag; the Texas Ratio `Stage 3 Gross NPLs / (Total Equity + Total Loan Loss
  Reserves)` (a genuinely bank-specific distress metric, >100% historically signals severe
  distress); and an **adapted Beneish M-Score proxy** — the standard model explicitly
  excludes financial institutions (Sales/Receivables/Gross-Margin/COGS don't translate to
  a bank balance sheet), so each component is substituted with a bank-equivalent concept
  (Total Operating Income for Sales, Net Loans for Receivables, NII/Deposits as a NIM proxy
  for Gross Margin, Cost-to-Income for SGAI, Other-Assets/Total-Assets for AQI), DEPI is
  omitted (no actual-year D&A breakdown disclosed), and the rendered section carries a
  prominent caveat that the original model's -2.22 threshold doesn't apply — interpret
  directionally only.

## 2026-07-06 structural review & rework

Compared the generated workbook cell-by-cell against `colossal-visuals/references/Blu
Containers Model - Vertical Complete.xlsx` (the actual FMI reference, not just its
documented conventions). Findings and what changed as a result:

- **Live scenario switch** — the reference has a single `Scenarios!$D$6`-style switch
  (`CHOOSE()`-driven) that makes any of Base/Best/Worst the fully-live Model sheet.
  **Built the same mechanism**: `SWITCH_CELL_REF = 'Scenarios'!$D$5`; every scenario
  -dependent assumption (loan growth, IFRS 9 loss rates, deposit growth, opex escalation)
  now renders as 4 rows (Base hardcoded, Best/Worst = Base × a multiplier cell, ACTIVE =
  `CHOOSE(switch, base, best, worst)`), and Model-sheet formulas reference the ACTIVE row.
  A "CURRENTLY RUNNING: X SCENARIO" banner (Model sheet, row 1) mirrors the reference
  exactly.
- **Multi-scenario Summary is static in the reference too** — confirmed its Base/Best/Worst
  Summary cells are bare hardcoded floats despite the rest of the workbook being live
  (makes sense: only one scenario is ever "live" at a time under the CHOOSE design, so
  showing all three needs a snapshot). Our Python-computed static Best/Worst was already
  the same solution to the same constraint — no change needed there.
- **Font color convention verified correct** — cell-by-cell confirmed the reference uses
  exactly blue/default-black/teal for input/formula/cross-ref, matching our
  `BLUE_INPUT`/`DARK`/`TEAL` tiers exactly. Our added `ORANGE` tier (modeled proxy) is our
  own extension, no conflict.
- **Visual style, Master Check placement** — reference uses zero colored fills anywhere
  (plain white, bold text, borders for totals) and an inline bare-number check; ours uses
  colored section bars and a top-of-sheet OK/ERROR panel. **Decision: keep our style** —
  explicitly chosen over matching the reference's plainer look.
- **Projection period & opening basis changed**: YEARS is now 2026-2030 (was 2024-2028);
  opening balance sheet moved from FY2023 to **FY2025 actual** (the 4 previously-broken
  Family Bank PDFs are now fixed/re-downloaded). All `LOAN_SEGMENTS`/`DEPOSIT_TYPES`/
  `INVESTMENT_SECURITIES`/`CAPITAL`/`PPE`/`OPEX_ITEMS` opening figures recalibrated to the
  real FY2025 balance sheet and income statement (see `research_output.md`'s
  "Update 2026-07-06" section for the full source figures).
- **Real peer data**: `data/` was reorganized into per-bank subfolders with re-downloaded
  annual reports for Family Bank + 9 peers. NCBA's P/B (1.2x) is now directly disclosed;
  I&M's (~0.64x) is computed from disclosed book value per share and share price. The
  other 7 peers remain `[PLACEHOLDER]` — searched each bank's FY2025 report for book
  value/price/market cap; not found as extractable text (likely infographic images).
  Beta remains a reasoned proxy (~1.0, frontier-market bank equity betas typically
  0.8-1.1x) — no market-data API available here for a true regression.

This is the design source of truth. Update it when a design decision changes, not just when
code changes. If this document and the code disagree, that's a bug in one of them — fix the
drift, don't let it linger.

## Context

The goal: a **repeatable bank/financial-institution model generator**, first applied to
Family Bank Kenya (a real NSE-listed bank), producing an audit-ready, fully-formula-linked
Excel workbook that ends in an **equity valuation** — not a static repeat of numbers we
already have elsewhere.

## Key decisions

1. **Modeleon spiked and rejected — building on `xl_helpers.py`.** Modeleon (real,
   Apache-2.0, v0.1.3) genuinely emits live formulas with working recurrence and
   cross-sheet references. But its Excel writer (`modeleon/compile/excel/writer.py:253-259`)
   only wires `number_format` through to cells — `bold`/`bg`/`font_color` passed to
   `set_style()` are silently dropped — and its layout engine is rigid (one row per
   Variable, fixed label/data columns), incompatible with the FMI vertical convention. The
   calculation/formula layer is built with the proven `xl_helpers.py` string-formula
   helpers instead (full control over layout and formatting).
2. **Full prudential/regulatory fidelity** — CAR, IFRS 9 provisioning, liquidity ratio,
   segmented loan book — not just an illustrative P&L/BS.
3. **Calibrate to Family Bank Kenya's real published financials** — primary source is the
   repo's own `data/` folder (see below), not secondary web summaries.
4. **Build it as a reusable generator** — a `bizplan` package (`bank_calculations.py` +
   `bank_excel_renderer.py` + a `config.py` convention), so the next bank engagement just
   swaps the config rather than rewriting the schedules/renderer.
5. **The end goal is an equity valuation.** DDM (primary) + Residual Income/Excess Return
   Model (cross-check) + P/B-ROE regression & P/E peer multiples (market sanity check) —
   standard practice for banks, since a plain FCFE/FCFF DCF fights with the fact that
   regulatory capital retention *is* the reinvestment decision for a bank. Cost of equity
   via CAPM with Kenya-specific inputs (Kenyan government bond yield, Damodaran's Kenya
   country risk premium, beta from Family Bank/peer Kenyan banks).
6. **Full ratio disclosures on the Outputs/Summary sheet** — CAMELS-complete: profitability
   (ROE, ROA, NIM, cost-to-income, DuPont ROA decomposition), capital adequacy (core/total
   capital ratios), liquidity (statutory liquidity ratio), cash flow ratios.

## Data sources

**`data/` (repo root)** — the primary calibration source:
- `Integrated-Report-Financial-Statements-2021-1.pdf` … `-2025.pdf` — five years of audited
  annual reports. Source for the real IFRS 9 note (stage split, ECL roll-forward, cost of
  risk), segment/sector loan breakdown, and multi-year trend data.
- `Family-Bank_MTN-_Information-Memorandum.pdf` — Medium Term Note info memorandum; likely
  has more granular risk-factor and credit-risk disclosure than the annual report.
- `FBL_LISTING_ABRIDGED_NEWSPAPER_FINAL-1.pdf`, `ke-fmly-2026-ps-00.pdf` — IPO/listing
  prospectus documents; likely contain the valuation basis used for the listing, peer
  comparisons, and share pricing rationale — useful for the Valuation sheet.

**Environment**: repo-root `.venv` (Python 3.13.2) now has `bizplan` (editable),
`openpyxl`/`python-docx`/`python-pptx`/`anthropic`/`click`, plus `pypdf`/`pdfplumber`/
`pymupdf`/`pikepdf` for PDF extraction/repair.

**Data quality finding**: 4 of 8 `data/` PDFs are broken (need re-downloading by the user)
— see `examples/family_bank_kenya/research_output.md` for the full
diagnosis. The 2023 annual report and the MTN Information Memorandum 2026
(`ke-fmly-2026-ps-00.pdf`, covers FY2021-2025 with peer comparables and sector outlook)
are fully usable and are the source for the research pulled so far.

**Working practice**: don't read these PDFs cover-to-cover. Extract text/tables once, then
search the extracted text for the handful of terms that matter ("Stage 1"/"Stage 2"/
"Stage 3", "expected credit loss", "non-performing", "capital adequacy", "liquidity ratio",
"segment information", "core capital") and jump straight to those pages. File size should
not translate into token spend — targeted lookup, not exhaustive reading.

**Secondary research already pulled** (web search, cross-check only — not calibration of
record): Family Bank Kenya FY2025 — total assets KES 208.7bn (+23.9%), net loans KES 105.9bn
(+14.0%), customer deposits KES 151.88bn (+20.1%), net interest income KES 15.63bn (+46.1%),
gross NPLs KES 17.56bn (+21.5%), total capital/RWA 19.6% vs. ~14.5% regulatory minimum, PAT
KES 5.38bn (+55.4%). CBK: Basel III-style LCR/NSFR ≥100% guidelines exist; exact current
core-capital/liquidity minimums need pulling from the CBK Prudential Guidelines PDF directly.

## Analytical framework (sell-side / buy-side practice)

- **CAMELS** (Capital, Asset quality, Management, Earnings, Liquidity, Sensitivity to
  market risk) — the Ratio Disclosures block should let a reader answer each CAMELS letter.
- **DuPont ROE decomposition for banks**: ROE = ROA × Equity Multiplier; ROA = NIM +
  non-interest income ratio − cost ratio − provision ratio − tax ratio (all as % of average
  assets). Explains *why* ROE moved, not just that it did.
- **Quality-of-earnings skepticism on provisioning**: credit costs should be sense-checked
  against a through-the-cycle norm (Family Bank's own 2021-2025 trend from `data/`), not an
  extrapolation of the latest benign year — provisioning is a common earnings-smoothing lever.
- **Loan concentration / funding stability**: segment/sector concentration and CASA ratio
  vs. term/wholesale funding, flagged as risk factors in the Assumptions sheet if high.
- **Why DDM + Excess Return, not FCFE** (Damodaran, *"Valuing Financial Service Firms,"*
  NYU Stern): regulatory capital retention is the reinvestment decision for a bank, so FCFE
  is unreliable; DDM and Excess Return/Residual Income are the standard tools.
- **P/B-ROE regression, not flat peer-average P/B**: the P/B-ROE relationship is empirically
  strong for banks (Damodaran) — read off Family Bank's implied P/B at its own ROE from a
  regression across the peer set, a more defensible cross-check than a simple average.

## Schedule design (`bizplan/financial/bank_calculations.py`)

Config-driven functions (mirrors `calculations.py`'s shape: accept a `config` module,
return plain dicts of lists), computed per year for the Base Case:

1. **Loan Book / Staging Schedule** — per segment (Retail/MSME/Corporate/Mortgage): opening
   gross exposure by Stage 1/2/3, new originations (Stage 1), stage transfers via a
   transition matrix, write-offs, closing gross exposure by stage.
1b. **IFRS 9 ECL / Provisioning Schedule** — PD/LGD/EAD by stage and segment, forward-looking
    macro overlay, ECL roll-forward, resulting P&L impairment charge and BS allowance. See
    "IFRS 9 provisioning design" below.
2. **Investment Securities Schedule** — government securities balance + yield.
3. **Deposit/Funding Schedule** — per type (demand/savings/term/wholesale): opening, growth,
   closing, cost of funds.
4. **Interest Income** — loan yield × avg loans (by segment) + securities yield × avg
   securities.
5. **Interest Expense** — cost of funds × avg deposits by type + cost of borrowings.
6. **Net Interest Income & NIM** = NII / average earning assets.
7. **Non-Interest Income** — fees & commissions, forex income, other.
8. **Operating Expenses** — staff costs, premises, technology, other; cost-to-income ratio.
9. *(Provisioning P&L charge comes from Schedule 1b, feeds straight into the IS.)*
10. **Income Statement** — NII + non-interest income − opex − provisions = PBT → tax → PAT.
11. **Cash Flow Statement** (indirect) — PAT + provisions + D&A ± Δloans ± Δdeposits ±
    Δsecurities = operating; capex = investing; dividends/capital = financing.
12. **Balance Sheet** — Assets (cash & balances with CBK, securities, net loans, PP&E,
    other); Liabilities (deposits, borrowings, other); Equity (share capital, retained
    earnings, statutory reserve).
13. **Capital Adequacy** — Core Capital (Tier 1) = share capital + retained earnings −
    intangibles; Total Capital = Tier 1 + Tier 2; RWA = risk-weighted loans + off-balance
    sheet; Core/Total Capital Ratio vs. CBK minimums.
14. **Liquidity** — liquid assets / total deposits vs. CBK statutory minimum.
15. **Ratio Disclosures** — CAMELS-complete profitability (incl. DuPont decomposition),
    capital adequacy, liquidity, cash flow ratios.
16. **Valuation** — CAPM cost of equity; DDM (multi-stage + Gordon terminal value);
    Residual Income/Excess Return cross-check; P/B-ROE regression + P/E peer multiples.

**Scoping rule**: only the Base Case gets full formula-linked treatment on the Model sheet.
Best/Worst remain Python-computed static comparison values on the Scenarios sheet — bounds
the work to one fully-live case instead of three.

### IFRS 9 provisioning design — disclosed vs. modeled

Public disclosure (annual report IFRS 9 note + CBK quarterly disclosure) realistically
gives us, at the aggregate level: gross NPLs, total loan loss allowance, cost of risk, and
the CBK 5-category classification (Normal/Watch/Substandard/Doubtful/Loss) that maps loosely
onto Stage 1/2/3. It essentially never gives us the stage-transition matrix, segment-level
PD/LGD/EAD, or the macro-sensitivity coefficients — those are proprietary. So the schedule
is built in two clearly separated layers:

1. **Calibration anchors (disclosed facts)** — opening gross NPLs, total ECL allowance, cost
   of risk trend, CBK classification split. Year-1 stage split and starting ECL coverage are
   *reverse-engineered* to tie to these disclosed totals, not invented independently.
2. **Modeled mechanics (benchmark/analyst-judgment, distinctly tagged)** — stage transition
   matrix, PD term structure (12-month Stage 1, lifetime/marginal Stage 2/3), LGD by segment
   (Basel standardized proxies: ~35–45% unsecured retail/MSME, ~20–30% mortgage), EAD/CCF on
   undrawn commitments, macro-sensitivity coefficients. Every such row carries a `source`
   note, e.g. `"Modeled — Basel standardized LGD proxy, not company-disclosed"`.

**Data-provenance color convention** (extends the FMI blue/black/green code in
`xl_helpers.py`): a fourth text color for "Modeled proxy, not disclosed" assumption cells,
with a legend on the Assumptions sheet — so a reader can visually distinguish hard facts
from analyst judgment at a glance.

**Mechanics** (per segment, or portfolio-level if segment staging isn't disclosed at that
granularity — decide during the research pass):
- Roll-forward gross exposure by stage: opening + new originations (Stage 1) − transfers out
  + transfers in − write-offs = closing, via the transition matrix.
- ECL per stage: Stage 1 = 12-month PD × LGD × EAD; Stage 2/3 = lifetime PD × LGD × EAD,
  discounted at the effective interest rate over remaining expected life.
- **Forward-looking macro overlay**: 3 macro scenarios (Base/Upside/Downside) from Kenya
  forward indicators (GDP growth, inflation, CBK rate outlook, KES/USD), probability-weighted
  (e.g. 60/20/20), each scaling PD by a sensitivity factor
  (`PD_scenario = PD_base × (1 + sensitivity × macro_deviation)`). This overlay should also
  drive the existing Base/Best/Worst scenario matrix (loan growth, NPL trend, cost of
  funds) — one macro assumption set feeding both.
- **Implemented as a stock, not a rolling allowance**: each stage's ECL is recomputed every
  period as `loss_rate x closing_gross_balance`, where `loss_rate` is calibrated directly
  from Family Bank's own disclosed FY2023 stage-level ECL/Gross ratios (not a separate
  PD x LGD split — disclosure doesn't support that split at this granularity). Under this
  approach a write-off's effect on the allowance is already embedded in the smaller
  post-write-off closing balance, so the correct non-double-counting P&L charge is simply
  **the period-over-period change in the ECL stock** (`ecl_total[i] - ecl_total[i-1]`) —
  not the textbook `change + writeoffs - recoveries` formula, which would double-count
  once write-offs are already netted into the stock. Proved algebraically (and confirmed
  empirically — see CHANGELOG) that this makes the balance sheet tie out exactly.
- Balance sheet: Gross Loans (Stage 1+2+3) − Total ECL Allowance = Net Loans. Off-balance
  sheet ECL sits as a separate provision in Other Liabilities, not netted against assets.
- Disclosure ratios: Stage 3 (NPL) coverage = Stage 3 ECL / Stage 3 gross loans; total
  coverage = total ECL / total gross loans; cost of risk = P&L impairment charge / average
  gross loans.

## Renderer design (`bizplan/financial/bank_excel_renderer.py`)

Sheet order: Cover, Summary, Assumptions, Scenarios, Model, **Valuation**. Built on shared
primitives in `bizplan/financial/xl_helpers.py` (`fill`, `font`, `align`, `write`, `num`,
`pct`, `header_row`, `section_header`, `year_header_row`, `data_row`, `total_row`,
`blank_row`, and the formula helpers `_cell`/`_sum_f`/`_add_rows_f`/`_sub_f`/`_ratio_f`/
`_ref_f`/`_model_ref`). All Model-sheet calculated rows are formula strings, threaded
through a `row_refs` dict (referenced as `M` in the code, and `A` for the parallel
Assumptions-sheet reference dict) so later formulas can reference earlier rows/cells by
key instead of a hardcoded address.

- **Master Check section** (top of Model sheet): Balance Sheet check
  (Assets − Liabilities − Equity = 0), Capital Adequacy check (vs. CBK minimum), Liquidity
  check (vs. CBK minimum) — each an `IF` formula showing "OK"/"ERROR" with conditional
  formatting (green/red).
- **Assumptions sheet**: four-color data-provenance convention (disclosed / modeled-
  benchmark / macro-forecast / analyst-judgment), with a legend.
- **Summary sheet**: adds a "Ratio Disclosures" block (Schedule 15) alongside the existing
  revenue/EBITDA KPI blocks.
- **Valuation sheet**: CAPM cost-of-equity inputs, DDM (live-linked to Model sheet dividend/
  PAT rows), Residual Income cross-check, P/B-ROE regression + P/E peer-multiples table —
  implied share price/equity value from all methods shown side by side.

## Project structure

Everything lives at the repo root — no pip-install/packaging ceremony. Every script does a
`sys.path.insert` of the repo root, so `bizplan` is importable without an editable install.

```
financial_model_template/
├── BLUEPRINT.md, BACKLOG.md, CHANGELOG.md, CLAUDE.md   ← tracking docs (repo root)
├── data/                                                ← source PDFs (Family Bank Kenya)
├── .venv/                                               ← shared virtual environment
├── bizplan/
│   ├── config_loader.py            ← load_and_validate() / validate_bank_config()
│   └── financial/
│       ├── xl_helpers.py           ← formula-capable openpyxl primitives
│       ├── bank_calculations.py    ← all 16 schedules, Python ground truth + scenarios
│       └── bank_excel_renderer.py  ← builds the live-formula workbook
├── examples/
│   └── family_bank_kenya/
│       ├── config.py               ← single source of truth for assumptions
│       └── research_output.md      ← calibration research, sourced and dated
├── output/                                              ← gitignored; timestamped run folders
│   └── 2026-07-06_151703/
│       ├── Family_Bank_Kenya_Financial_Model.xlsx      ← that run's generated workbook
│       └── config.py                                    ← exact copy of the config that produced it
└── scripts/
    ├── build_bank_model.py         ← entry point: config → calc → render → save
    ├── launch.sh                   ← Unix/macOS/Linux launcher
    ├── launch.bat                  ← Windows launcher
    └── requirements.txt            ← runtime deps (openpyxl)
```

**Launchers** (`scripts/launch.sh`, `scripts/launch.bat`) are the intended entry point —
only these two, no PowerShell variant. Both do the same three things in order:
1. Check for `.venv/` at the repo root; if it doesn't exist, create it
   (`python -m venv .venv` / `python3 -m venv .venv`).
2. Activate it.
3. Install/upgrade `scripts/requirements.txt` into it, then run
   `scripts/build_bank_model.py`.

This means a fresh clone with nothing set up can just run `./scripts/launch.sh` (or
`scripts\launch.bat` on Windows) and get a built workbook — no manual venv setup, no
assumption that dependencies are already installed. `scripts/build_bank_model.py` itself
stays runnable directly too (`.venv/bin/python scripts/build_bank_model.py`) for anyone who
already has the venv active — the launchers are a convenience wrapper, not the only path in.

**Output folder convention** (matching `colossal-visuals`, checked directly against its
`scripts/launch.sh` and `output/` folder): each launcher run creates a timestamped
subfolder under `output/` (`output/<YYYY-MM-DD_HHMMSS>/`) containing that run's generated
`.xlsx` plus an exact copy of the `config.py` that produced it — every run is a
reproducible snapshot. `build_bank_model.py` reads the `OUTPUT_DIR` env var (which the
launcher sets); running it directly without a launcher falls back to writing straight into
`examples/family_bank_kenya/`, same as before this convention existed. **Never hand-edit
files in `output/`** — they're regenerated every run; all changes go into `config.py`.
`output/` is already covered by the root `.gitignore` (unanchored `output/` pattern, so it
catches this folder at any depth).

## Verification

- Open the `.xlsx`, click into calculated cells, confirm live formulas (`=SUM(...)`,
  `=H12/H5`), not values.
- Master Check section shows "OK" for Balance Sheet, Capital Adequacy, Liquidity (Base Case).
- Year 1 Base Case figures are plausible against the `data/`-derived research figures.
- Best/Worst scenario columns still render (static values, as designed).
- Valuation sheet's three methods each produce a plausible implied value, and DDM/Residual
  Income formulas trace live back to the Model sheet (not re-typed).

## Open follow-ups (not blocking)

- CLI wiring for the bank path if a nicer UX than the launchers is ever needed.
- Deeper CBK compliance detail (single-borrower limits, sector concentration limits) if a
  future engagement needs it.
