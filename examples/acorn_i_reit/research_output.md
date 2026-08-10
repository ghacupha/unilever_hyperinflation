# Acorn I-REIT — calibration research

Primary data source for calibration is `data/KENYA REITS AND REOCS EQUITY ANALYSIS REPORT.pdf`
(sector-wide summary, dated 2026-08-06) plus Acorn Student Accommodation I-REIT's own
`ASA I-REIT 2025 Semi-Annual Report` (fetched 2026-08-09 from
`acornholdingsafrica.com/wp-content/uploads/2025/08/ASA-I-REIT-2025-Semi-Annual-Report.pdf`),
which contains full unaudited consolidated interim financial statements for the six months
ended 30 June 2025 with Dec-2024 and Jun-2024 comparatives, plus a historical NAV/unit series
back to 2021 inception. CMA regulatory limits are from
`cma.or.ke/wp-content/uploads/2023/03/REITS.pdf` ("FAQs: Real Estate Investment Trusts").

All figures below are as originally disclosed in **KES '000** unless noted; the config converts
to **KES millions** (`CURRENCY_UNIT_ABBR = "KES Mn"`) to match this repo's existing convention.

Provenance tags follow the convention established for the Family Bank build:
`[DISCLOSED]` (straight from the filings), `[DISCLOSED-DERIVED]` (computed from disclosed
figures), `[MODELED]` (analyst-judgment proxy/interpolation, flagged), `[MACRO]` (forward-looking
macro assumption), `[PLACEHOLDER]` (illustrative, flagged for replacement).

## 2026-08-09 — Initial REIT-domain calibration (pivot from Family Bank Kenya)

### Regulatory framework (CMA I-REIT-specific limits)
- Borrowing/gearing limit: **35% of total asset value**; up to 40% with unit-holder ordinary
  resolution, temporary ≤6 months, no extension. `[DISCLOSED]` — CMA REITs FAQ Q7, cross-checked
  against Acorn's own reported LTV commentary ("comfortably below the regulatory limit of 35%").
- Minimum 75% of NAV (TAV per the regulation text itself) in income-producing real estate within
  2 years of authorization; ≥70% of income from eligible investments after year 2. `[DISCLOSED]`
  — CMA REITs FAQ Q7, corroborated by Acorn's own Appendix 2 ("Asset Holdings Versus Prescribed
  Limits") showing 98% actual against a 75% minimum.
- Minimum initial assets for an I-REIT: KES 300 million. `[DISCLOSED]` — CMA REITs FAQ Q6.
- Distribution: **≥80% of taxable/net income** to unit-holders. `[DISCLOSED]` — CMA REITs FAQ
  (benefits section). Acorn's own FY2025 payout of 34.1% is reported by the sector analysis as
  *below* this minimum — a real governance flag carried into `Sources`/`Assumptions`, not
  smoothed over.
- Minimum 7 investors; promoter must retain 20% of NAV in year 1, 10% in year 2 (I-REIT).
  `[DISCLOSED]` — CMA REITs FAQ Q9/Q13.
- Restricted-REIT minimum investment: KES 5 million. `[DISCLOSED]` — CMA REITs FAQ Q11, matches
  the sector report's own statement of the same figure.

### Property portfolio (as at 30 June 2025)
7 properties, purpose-built student accommodation (Qwetu brand), 4,466 beds (sums to the
"~4,500 beds" headline). `[DISCLOSED]` — interim report "Portfolio Overview" + "Details of
Valuation":

| Property | Location | Rooms | Beds | Fair value Jun-25 (KES'000) |
|---|---|---|---|---|
| Qwetu Jogoo Road | Jogoo Lane | 343 | 502 | 817,000 |
| Qwetu Ruaraka | Outer Ring Road | 380 | 543 | 834,000 |
| Qwetu Wilsonview | Keri Road | 512 | 728 | 2,033,000 |
| Qwetu Parklands | Kipkabus Road | 335 | 533 | 1,219,000 |
| Qwetu Aberdare Heights I | USIU Road | 518 | 697 | 1,944,000 |
| Qwetu Hurlingham | Argwings Kodhek Road | 583 | 834 | 2,391,000 |
| Qwetu Aberdare Heights II | USIU Road | 450 | 629 | 1,489,000 |
| **Total** | | **3,121** | **4,466** | **10,727,000** |

Sums exactly to the disclosed Investment Property total at 30 June 2025 (10,727,000) — a good
internal-consistency check.

### Actual years: FY2023, FY2024, FY2025

**FY2023 (thin)** — only balance-sheet snapshot and dividend total found in the sources
reviewed; income-statement detail not available and is `[MODELED]` (interpolated from the
FY2024 disclosed trend, not fabricated to false precision):
- Investment property at 31 Dec 2023: KES 8,776,600k `[DISCLOSED]` — note 7(a) "At 1 January"
  column of the Dec-2024 comparative.
- Total unit-holder equity (NAV) at 31 Dec 2023: KES 7,377,536k (Trust Capital 6,533,596 +
  Retained earnings 211,820 + Fair value reserves 632,120) `[DISCLOSED]` — statement of changes
  in equity, "At 1 January 2024" row (= FY2023 closing balance).
- NAV/unit at Dec-2023: KES 22.03 `[DISCLOSED]` — NAV-growth chart.
- Units in issue at Dec-2023: back-solved 7,377,536 / 22.03 ≈ 334.9M `[DISCLOSED-DERIVED]`; the
  Note 17 roll-forward's own "At 1 January 2024" figure of 327,880,290 is used instead for the
  Units schedule (see "known reconciliation gap" below) — a ~2% difference between the two,
  flagged rather than silently reconciled.
- Total dividends paid in FY2023: KES 241,000k (interim 87,000 + final 154,000) `[DISCLOSED]` —
  "Interim and Final Dividend" chart.
- Rental income, opex, net profit, debt for FY2023: `[MODELED]` — interpolated backward from the
  FY2024 actual using the disclosed FY2023→FY2024 dividend growth (241M→225M, roughly flat) and
  NAV growth (22.03→22.91, +4.0%) as the trend anchor.

**FY2024 (full)** — `[DISCLOSED]` throughout, from the interim report's Dec-2024 comparative
column of the primary statements:
- Balance sheet at 31 Dec 2024: Investment property 10,575,000; PP&E 6,505; Goodwill 477;
  non-current assets 10,581,982; current assets 496,174 (receivables 28,459; due from related
  parties 128,391; financial assets 2; inventories 471; cash 338,851); **total assets
  11,078,156**; Trust Capital 6,975,726; Fair value reserves 942,080; Retained earnings 204,281;
  **NAV 8,122,089**; Borrowings 2,650,766; payables 256,903; due to related parties 48,398;
  **total liabilities 2,956,067**.
- NAV/unit at Dec-2024: KES 22.91 `[DISCLOSED]`.
- Investment property roll-forward FY2024 (note 7(a)): opening 8,776,600 + additions 8,440 +
  acquisitions 1,480,000 + fair value gain 309,960 = closing 10,575,000.
- Equity roll-forward FY2024: opening 7,377,536 + unit issuance 442,130 + total comprehensive
  income 555,611 − transfer to non-distributable reserves (0 net) − final dividend (2023) paid
  154,104 − interim dividend (2024) paid 99,085 = closing 8,122,088.
- Total dividends paid in FY2024: KES 225,000k (interim 99,086 + final 125,643, the latter
  ratified at the April-2025 AGM for FY2024) `[DISCLOSED]`.

**FY2025 (full-year headline + H1 detail, H2 back-solved)**:
- Full-year net profit: KES 670.16M `[DISCLOSED]` — sector report, +20.6% YoY.
- Full-year (year-end) NAV/unit: KES 24.30 `[DISCLOSED]` — sector report.
- Full-year distribution: KES 208.5M total, KES 0.57/unit, **34.1% payout ratio — below the 80%
  regulatory minimum** `[DISCLOSED]` — sector report, flagged explicitly as a governance point.
- Full-year borrowings: reduced from KES 2.5Bn to KES 1.9Bn (avg rate 17%→11.1%) `[DISCLOSED]` —
  sector report, corroborated by the interim report's own forward note ("ASA I-REIT debt was
  further reduced by KES 400 million in July, bringing the total debt portfolio to KES 1.91
  billion").
- H1 2025 (30 June 2025) is fully disclosed (see below); **H2 2025 is back-solved** as
  FY2025-total minus H1-actual, `[DISCLOSED-DERIVED]`:
  - H2 net profit = 670,160 − 251,633 = **418,527**
  - H2/final distribution = 208,500 − 102,626 = **105,874**
- Dec-2025 closing balance sheet (investment property, total assets, units in issue, payables)
  is not disclosed at this granularity anywhere in the sources reviewed and is **`[MODELED]`**,
  anchored to the disclosed control totals (NAV/unit 24.30, net profit 670.16M, debt ~1.91Bn):
  units in issue modeled to continue the H1 2025 issuance pace at roughly half rate in H2 (the
  2025 Supplemental Offer's discount window closed 30-Jun-2025, so a slower pace is expected)
  → ≈374.5M units; NAV rolled forward from the Jun-2025 actual (8,617,808) + H2 net profit
  (418,527) + modeled H2 unit-issuance proceeds (≈192,000) − the H1-2025 interim distribution
  paid in H2 (102,626) → ≈9,125,709, which implies NAV/unit ≈24.37 — within 0.3% of the
  disclosed 24.30, a reasonable cross-check for a modeled figure.

### H1 2025 interim financial statements (30 June 2025) — fully `[DISCLOSED]`
- Income statement: Rental revenue 524,101 (Residential 516,440 + Retail 7,661) + other income
  267 = Operating income 524,368; less admin expenses 178,460, fund opex 56,243, plus impairment
  reversal 3,306 = Operating profit 292,972; + finance income 9,664 − finance costs 202,703 +
  fair value gain 151,701 = **Net profit 251,633**.
- Distributable income reconciliation: Net profit 251,633 − impairment reversal 3,306 − fair
  value gain 151,701 = Distributable income 96,625 (+ retained earnings b/fwd 6,168 → proposed
  interim distribution 102,626, KES 0.29/unit).
- Balance sheet at 30 June 2025: Investment property 10,727,000; total assets 11,340,001; Trust
  Capital 7,346,100; Fair value reserves 1,093,781; Retained earnings 177,927; **NAV 8,617,808**;
  Borrowings 2,419,889; **total liabilities 2,722,193**.
- Debt roll-forward (note 14): opening 2,650,766 + additions 3,810,000 + interest accrued
  109,889 + interest expense 92,816 − principal repayment 4,000,000 − interest paid 243,582 =
  closing 2,419,889 (verified to the cent).
- Units-in-issue roll-forward (Note 17 / "Outstanding REIT holdings movement"): opening (1 Jan
  2025) 349,008,896 + issued 17,513,714 = closing (30 Jun 2025) **366,522,610**.
- Weighted average cost of debt: 16.3% (Jan-2025) → 13.3% (Jun-2025) → 11.1% (current, per the
  report's own forward note), following a Q2-2025 refinancing.
- LTV: 21% (Jun-25) vs 24% (Jun-24), against the 35% regulatory ceiling.
- Ratios directly reported by Acorn itself (used as the model's ratio-disclosure set almost
  verbatim): MER 0.5%, Interest Coverage Ratio 1.4x, Fund Operating Margin 56%, Adjusted EPS
  0.27, Annualized Distribution Yield 2.5%, Annualized Capital Appreciation 2.9%, Total Return
  5.4%.

### Known reconciliation gap — units in issue vs reported NAV/unit
Cross-multiplying the disclosed NAV totals against the disclosed units-in-issue roll-forward
does not exactly reproduce Acorn's own reported "NAV per unit" headline figure:
- Dec-2024: NAV 8,122,089 ÷ units 349,008,896 (Note 17 "beginning of Jan-25" balance) = 23.27
  implied, vs 22.91 disclosed (~1.6% gap).
- Jun-2025: NAV 8,617,808 ÷ units 366,522,610 = 23.51 implied, vs 23.24 disclosed (~1.2% gap).

This is a small, consistent (~1-2%) gap across both period-ends, most likely explained by
Acorn's own NAV/unit calculation using a weighted-average unit count over the period (common for
per-unit metrics) rather than the point-in-time closing balance used by the register roll-forward
— not a data error to "fix" by picking one number and forcing a match. The model uses the
[DISCLOSED] units-in-issue roll-forward (it's the most explicitly labeled, purpose-built table)
to drive its own live NAV/unit formula, and separately carries Acorn's own reported NAV/unit
figures for the Summary/ratio-disclosure rows — so the model's *computed* NAV/unit will land
within ~1-2% of Acorn's own reported figure in the actual-year columns, which is expected and
documented rather than hidden.

### Peer REIT comparables (for NAV discount/premium and cap-rate cross-checks)
`[DISCLOSED]` — sector report §5.3 "Valuation Metrics":
| REIT | NAV/unit | Trading price | Discount/(premium) |
|---|---|---|---|
| Acorn I-REIT | 24.30 | 23.24 | -4.4% |
| LAPTRUST Imara I-REIT | 17.20 | 20.00 | +14.0% |

Sector-wide returns comparison (2024 / H1 2025), for context in Assumptions: REITs 7.0%/2.7%;
NSE equities 34.0%/51.0%; 10-year government bonds 12.4%-13.6%/—. `[DISCLOSED]` — sector report
§5.2.

### CAPM inputs (cost of equity, for the DDM leg of the blended valuation)
- Kenya 10-year government bond yield (risk-free rate): **11.29%** (24 March 2026, an
  11.5-year low, consistent with the CBR easing cycle Acorn's own interim report describes —
  CBR 10.75%→9.75% in H1 2025). `[DISCLOSED]` — Trading Economics, via web search 2026-08-09.
  Lower than the 12.32% used in this repo's prior Family Bank calibration (2026-07-02), which is
  expected given continued monetary easing over the intervening months.
- Kenya total equity risk premium: **13.94%** (Damodaran country risk premium dataset, January
  2026 update). `[DISCLOSED]` — reused from this repo's own prior Family Bank calibration
  (`BACKLOG.md`, 2026-07-26 entry, sourced from Damodaran's published dataset); not re-fetched
  fresh this session but the underlying dataset is dated and unlikely to have moved materially
  in a few weeks.
- Beta: **no REIT-specific beta available.** Acorn I-REIT trades on the NSE's restricted
  Unquoted Securities Platform with thin secondary-market liquidity, precluding a reliable beta
  regression — the same category of constraint the Family Bank calibration hit with its own
  too-newly-listed peer set. `[PLACEHOLDER]` — 0.65, a defensive-moderate proxy typical of
  regulated income-generating real estate (lower than typical equity beta, reflecting REITs'
  bond-like distribution profile), flagged for replacement once a usable beta source is found.
  This also supports weighting NAV and cap-rate approaches more heavily than DDM in the blended
  valuation, since the DDM leg rests on the weakest-sourced input.

### Not yet pulled
- LAPTRUST Imara I-REIT's, ILAM Fahari I-REIT's, ALP Industrial REIT's and TRIFIC Green USD
  I-REIT's own full financial statements — only sector-report summary figures available so far.
  Only needed once the model is extended to a second REIT instance (per the user's stated
  intent to "use it to value other REITs" later).
- A REIT-sector-specific cap rate for direct-capitalization valuation — not directly disclosed
  anywhere in the sources reviewed; the model derives an implied cap rate from Acorn's own H1
  2025 NOI and disclosed investment property fair value (NOI run-rate ÷ fair value) as a
  `[DISCLOSED-DERIVED]` starting point rather than assuming an external market cap rate.
