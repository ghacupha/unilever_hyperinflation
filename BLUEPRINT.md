# Blueprint: REIT Valuation Model

**Status:** Pivoted 2026-08-09 from a Family Bank Kenya-specific banking model to a generic
REIT (Real Estate Investment Trust) valuation model, first instance Acorn I-REIT (NSE-listed,
Kenya). The prior banking-model design history lives in git history and in `CHANGELOG.md`'s
earlier entries — this file starts fresh for the REIT domain rather than merging the two;
they share no calculation logic (only the generic `bizplan/config_loader.py` load/validate
pattern and `bizplan/financial/xl_helpers.py`'s formula/styling primitives carried over).

## Why a REIT is a different domain, not a bank re-skin

A bank's economics center on a loan book (IFRS 9 staged provisioning), deposits (net
interest income), and regulatory capital adequacy. None of that applies to a REIT. A REIT
holds income-generating property, earns rental income, and is legally required to
distribute most of its income to unit-holders rather than retain it as a growth-equity
would. The schedules, the regulatory framework, and the valuation methodology are all
different — this is a full rewrite of the calculation and rendering layers, reusing only:

- `bizplan/config_loader.py` — the load/validate pattern (`REQUIRED_FIELDS`,
  `validate_reit_config`, `load_and_validate`)
- `bizplan/financial/xl_helpers.py` — formula-capable openpyxl primitives (colors,
  `header_row`/`data_row`/`total_row`, `_cell`/`_sum_f`/etc. formula-string helpers), and
  the FMI data-provenance color convention (blue = disclosed input, dark = internal
  formula, teal = cross-sheet reference, orange = modeled/benchmark proxy)
- The overall sheet architecture: Cover / Summary / Assumptions / Scenarios / Model /
  Output / Sources, a Master Check block, and a single scenario-switch cell
  (`Scenarios!$D$5`, 1=Base/2=Best/3=Worst) that every scenario-dependent Assumptions row
  resolves to via `CHOOSE()`, so flipping it live-recalculates the whole Model sheet.

## Regulatory framework (CMA I-REIT-specific)

Source: `cma.or.ke/wp-content/uploads/2023/03/REITS.pdf` ("FAQs: Real Estate Investment
Trusts"), cross-checked against Acorn's own reported compliance figures. Full citations in
`examples/acorn_i_reit/research_output.md`.

- **Gearing/borrowing limit**: 35% of total asset value; up to 40% with unit-holder
  ordinary-resolution approval, temporary ≤6 months, no extension.
- **Income-producing real estate minimum**: 75% of NAV within 2 years of authorization;
  ≥70% of income from eligible investments after year 2.
- **Distribution minimum**: ≥80% of taxable/net income to unit-holders.
- **Minimum initial assets**: KES 300 million (I-REIT).
- Minimum 7 investors; promoter must retain 20% of NAV year 1, 10% year 2.

These map directly onto the Model sheet's Regulatory Compliance section and the Master
Check's LTV / Income-Producing-% / Payout status rows (`_build_regulatory_section`,
`_build_master_check` in `bizplan/financial/reit_excel_renderer.py`).

## Config schema (`bizplan/config_loader.py`, `examples/<reit>/config.py`)

`REQUIRED_FIELDS`: `BUSINESS_NAME`, `OUTPUT_PREFIX`, `CURRENCY`, `CURRENCY_UNIT_ABBR`,
`YEARS`, `ACTUAL_YEARS`, `TAX_RATE` (0 — REITs are income-tax-exempt on qualifying property
income), `PROPERTIES` (list of dicts: name/location/rooms/beds/opening_fair_value —
generic enough for office/retail/industrial REITs, not just student housing),
`RENTAL_INCOME`, `OPEX_ITEMS`, `CAPITAL` (debt terms), `UNITS` (issuance),
`REGULATORY` (the CMA limits above, as config so a different jurisdiction/REIT type
could override them), `MACRO_SCENARIOS`, `SCENARIO_MULTIPLIERS`, `VALUATION` (CAPM inputs
+ cap rate + blend weights), `PEER_REITS`, `ACTUALS` (per-year dict, provenance-tagged).
Optional: `COVER_INFO`, `SOURCES` (both read defensively via `getattr` in the renderer).

## Schedule design (Model sheet)

Same "3 actual years immediately followed by 5 projected years" convention as the prior
banking model — actual-year INPUT rows are hardcoded facts (pinned to `config.ACTUALS`),
DERIVED/subtotal rows are live same-column formulas over those facts (so an actual-year
hand-edit still re-flows through every subtotal); projected-year rows are fully live
formulas referencing Assumptions-sheet driver cells or the prior column.

1. **Property Portfolio** — portfolio-*aggregate* fair-value roll-forward (opening +
   additions/acquisitions + fair value gain = closing). Deliberately aggregate, not
   per-property, across all 8 years: the source filings only give a per-property
   snapshot at one point in time (30 Jun 2025), not a multi-year per-property history, so
   a per-property 8-year roll-forward would be fabricated precision. The per-property
   snapshot itself is shown as a static reference table on the Assumptions sheet.
2. **Rental Income & NOI** — occupancy glides from the disclosed portfolio-blended H1
   2025 rate toward a stabilized target over a configurable recovery period; rental
   income grows with escalation × the occupancy path.
3. **Operating Expenses** — admin (property-level) + fund-level (management/trustee/
   custodian/CMA fees) opex, itemized in config from Acorn's own note structure.
4. **Debt / Gearing** — borrowings roll-forward, weighted-average interest rate, finance
   costs.
5. **Income Statement** — Operating Income → Operating Profit → (+finance income
   −finance costs +fair value gain) → Net Profit, matching Acorn's own statement
   structure exactly (see `reit_calculations.py`'s module docstring for how actual-year
   opex/finance-income are back-solved as a reconciliation residual against the pinned,
   disclosed Net Profit where the filings don't give item-level actual-year detail).
6. **Distributable Income & Distributions** — Net Profit minus non-cash items (fair
   value gain) = Distributable Income; × payout ratio (pinned to the real disclosed
   ratio in actual years — including where, as in FY2025, it's genuinely below the 80%
   CMA minimum, a real governance fact carried through rather than smoothed over) ÷
   units = DPU.
7. **Balance Sheet** — Total Assets = NAV + Total Liabilities is the *identity itself*
   for projected years (not an independent sum): NAV rolls forward from retained
   earnings + unit-issuance proceeds, Total Liabilities from the debt schedule, and
   Other Assets/cash is the residual plug — exactly how a real cash flow statement's
   closing cash balance is a residual, not an independently-forecast figure. (An earlier
   draft grew "other assets" independently of NAV and broke the Master Check's balance
   check for every projected year — fixed by making assets the identity, not a separate
   forecast.)
8. **Regulatory Compliance** — LTV, income-producing-%, both vs. the CMA minimums above.

## Valuation (Output sheet)

Blends three approaches (config-weighted, default NAV 40% / DDM 30% / cap rate 30% — NAV
weighted heaviest since it's the most reliable anchor for a property-holding entity, and
the DDM leg rests on the weakest-sourced input, beta):

- **NAV** — the latest projected-year NAV/unit, directly off the Balance Sheet.
- **DDM** — PV of *projected-year-only* DPU (2023-2025 are actual, already-paid
  distributions, not future cash flows to discount) + PV of **terminal NAV/unit**, not a
  pure Gordon-growth-on-dividends model. With payout ratios well below 100%, most of a
  REIT's total return accrues through NAV growth on retained earnings, not distributions
  alone, so terminal NAV/unit is the more defensible "exit value" than an infinite-growth
  dividend annuity — a real methodology choice made after an initial Gordon-growth version
  produced a DDM value 5x below NAV, an implausible divergence for a property-holding
  entity in equilibrium.
- **Direct capitalization / cap rate** — latest NOI run-rate ÷ cap rate = implied
  property value, less debt, ÷ units.
- **Peer cross-check** — this REIT's own NAV × the average peer NAV discount/premium
  (Acorn I-REIT vs. LAPTRUST Imara I-REIT, the only two Kenyan REITs with disclosed
  NAV-vs-trading-price figures found in research).

Cost of equity: CAPM (Kenya 10-year bond risk-free rate + beta × Kenya equity risk
premium). Beta has no reliable REIT-specific source (thin/restricted-market trading
precludes a regression) and is a flagged placeholder — see
`examples/acorn_i_reit/research_output.md`.

## Known simplifications (see `research_output.md` for full detail and citations)

- **Property Portfolio is portfolio-aggregate, not per-property**, across the projection
  (data availability, not a design preference — see above).
- **Opex item-level detail for the thin 2023/2024 actual years** is proportionally
  allocated from the FY2025 (H1 actual × 2) item-level base, scaled to the reconciled
  aggregate total — not independently disclosed at item level for those years.
- **FY2025's closing (31 Dec 2025) balance sheet is modeled**, anchored to three
  disclosed control totals (NAV/unit 24.30, net profit 670.16m, debt ~1,910.0m) — the
  filings reviewed give full detail only through the 30 Jun 2025 interim.
- **Units-in-issue vs. NAV/unit reconciliation gap**: cross-multiplying the disclosed
  units-in-issue roll-forward against disclosed NAV doesn't exactly reproduce Acorn's own
  reported NAV/unit headline (~1-2% gap, both period-ends) — most likely a
  weighted-average-vs-point-in-time unit-count convention difference on Acorn's side, not
  a data error. Documented, not silently forced to match.

## Follow-up work (not in this pass — see `BACKLOG.md`)

The equity-research-report PDF pipeline (`bizplan/report/*`, SOPs under
`.devops/agents/equity-report/`) still imports the retired `bank_calculations`/
`bank_excel_renderer` modules and will not currently run. Its 6-stage `claude -p`
mechanics are domain-agnostic, but its SOP prose and JSON schemas speak bank language
(IFRS 9, CAR) and need a REIT-language adaptation pass.
