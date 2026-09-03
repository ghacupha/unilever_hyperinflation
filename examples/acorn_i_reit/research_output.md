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

### Not yet pulled (superseded 2026-08-25 — see dated section below for what's now sourced)
- ~~LAPTRUST Imara I-REIT's, ILAM Fahari I-REIT's, ALP Industrial REIT's and TRIFIC Green USD
  I-REIT's own full financial statements~~ — LAPTRUST Imara (3 full audited years) and ILAM
  Fahari (FY2025 audited + FY2024 comparative) are now fully sourced and ready for a
  `config.py` build. ALP Industrial only has a maiden H1 2026 interim (no full-year report
  exists yet). TRIFIC Green USD has no actuals at all yet (listed ~2 months ago) — genuinely
  not sourceable until it files its first annual report. Full detail below.
- ~~A REIT-sector-specific cap rate for direct-capitalization valuation~~ — still no single
  authoritative "Kenya REIT cap rate" is published, but real disclosed segment-level yields
  are now sourced as cross-checks (ILAM Fahari's own independent valuer's retail/office
  yields, ALP Industrial's industrial entry yields, general Nairobi residential yields).
  Acorn's own `[DISCLOSED-DERIVED]` implied cap rate (5.47%) remains the model's direct input
  — see cross-check below.

## 2026-08-25 — Comparative REIT actuals + sector cap rate cross-check

Researched to fill the two gaps above, per user request. All company-specific figures below
are `[DISCLOSED]` (straight from each REIT's own primary filings) unless tagged
`[DISCLOSED-DERIVED]`. No `config.py` changes made for these three REITs yet — that's a
larger follow-up (BACKLOG.md Phase 3/4), this pass is research-only. Acorn's own `cap_rate`
input in `config.py` is unchanged; the sector yields below are added as citation/cross-check
only.

### LAPTRUST Imara I-REIT — 3 years of audited actuals
Source: LAPTRUST Imara I-REIT's own audited financial statements, NSE-hosted PDFs, FY2023
(approved 7-May-2024), FY2024 (approved 25-Mar-2025), FY2025 (approved 30-Mar-2026).
Units-in-issue (346,231,413, constant all 3 years — no issuance since listing)
`[DISCLOSED-DERIVED]`, cross-checked: Trust Capital 6,924,628,260 ÷ 346,231,413 = exactly
20.00, the disclosed IPO price.

| | FY2023 | FY2024 | FY2025 |
|---|---|---|---|
| Net profit/(loss) | +57.2M | (204.3M) | (280.3M) |
| Profit before FV changes | 244.6M | 353.9M | 259.8M |
| Fair value adjustment | (187.4M) | (558.2M) | (540.1M) |
| Total equity (NAV) | 6,981.9M | 6,452.0M | 5,953.7M |
| NAV/unit `[DISCLOSED-DERIVED]` | 20.17 | 18.64 | 17.19 |
| Distribution paid | 195.7M | 283.1M | 207.8M |
| DPU | 0.57 | 0.82 | 0.60 |
| Payout ratio `[DISCLOSED-DERIVED]` | 80.0% | 80.0% | 80.0% |
| Investment property FV | 6,711.7M | 6,195.8M | 5,701.3M |
| Total assets | 6,762.3M | 6,300.5M | 5,806.3M |
| Borrowings | 0 | 0 | 0 |

Corrections to BACKLOG.md's prior framing: **not three consecutive loss years** — FY2023 was
profitable; the NAV-erosion/loss pattern is FY2024-FY2025 (two years), driven entirely by
investment-property fair-value markdowns (profit *before* FV changes was positive and growing
through FY2024). LAPTRUST hits the CMA 80% payout minimum exactly every year — a clean
contrast to Acorn's below-minimum 34.1% FY2025 payout. **Fully ungeared** (zero borrowings)
all three years, vs. Acorn's ~21-24% LTV. Dec-2025 NAV/unit (17.19) matches the sector
report's peer table (17.20) almost exactly, cross-validating both sources. Caveat on the
existing `PEER_REITS` +14.0% "premium" figure: trading price is locked at the Kshs 20.00 IPO
price by regulatory mandate (restricted-segment REIT), reported to run until March 2026 — this
may not reflect genuine market-clearing demand. Still not found: per-property portfolio detail
(the audited statements are one-page aggregate summaries; the REIT manager's full annual
report, which likely has a property schedule, wasn't reachable — sterlingreit.co.ke link
returned an error).

Sources: nse.co.ke/wp-content/uploads/Laptrust-Imara-I-REIT-*-Audited-Financial-Statements
(FY2023/FY2024/FY2025 PDFs, filed under NSE company disclosures).

### ILAM Fahari I-REIT — FY2025 audited actuals (+ FY2024 comparative)
Source: ilamfahariireit.com — condensed media-set financials and full 110-page annual report,
FY2025, approved 26-Mar-2026, Grant Thornton LLP unqualified audit opinion.

Property portfolio (30 Dec 2025), valued by Tysons Limited (independent, DCF + cost approach):

| Property | Location | Sector | FV 2025 | FV 2024 |
|---|---|---|---|---|
| Greenspan Mall | Nairobi, Block 82/8759 | Retail | 2,500.0M | 2,400.0M |
| 67 Gitanga Place | L.R. 3734/1426 | Office/light industrial | 650.0M | 650.0M (flat — largely vacant) |
| **Total** | | | **3,150.0M** | **3,050.0M** |

**Note 11 "unobservable inputs" — a real, independently-disclosed cap-rate cross-check**
(this is the closest thing to a formal Kenya REIT cap rate found in any source reviewed):

| | Retail 2025 | Retail 2024 | Office & light industrial 2025/2024 |
|---|---|---|---|
| Term yield | 13.0% | 12.5% | 12.5% |
| Reversionary yield | 9.0% | 9.0% | 9.0% |
| Discount rate | 13.0% | 12.5% | 12.5% |

NAV 3,748,424,278 (2025) vs 3,556,949,033 (2024) → NAV/unit **20.71** (2025) vs 19.65 (2024).
Net profit 245,766,935 (2025) vs 377,204,674 (2024) — decline from a smaller fair-value gain
(100.0M vs 263.6M). Distributable earnings 145,766,935 (2025) vs 62,128,812 (2024), +135% YoY.
Distribution 117,631,995 = 65¢/unit (2025) vs 54,291,995 = 30¢/unit (2024). Payout ratio
`[DISCLOSED-DERIVED]` 80.7% (2025) — meets the CMA 80% minimum, unlike Acorn. **Zero
borrowings**, LTV 0%. Units in issue 180,972,300, unchanged both years. Not found: trading
price / NAV discount-premium — Fahari delisted from the NSE Main Market in Feb-2024 and now
trades on the Unquoted Securities Platform with no market price disclosed in either document,
so it can't extend the `PEER_REITS` discount/premium table.

Sources: ilamfahariireit.com/final-results;
ilamfahariireit.com/assets/files/ILAM_Fahari_I-REIT-Condensed_Media_Set_Audited_Financials_FY2025.pdf;
ilamfahariireit.com/assets/files/ILAM_Fahari_I-REIT_Annual_Report_FY2025.pdf.

### ALP Industrial REIT — H1 2026 interim (maiden reporting period, USD-denominated)
CMA-authorized 8-Dec-2025, NSE-listed 11-Mar-2026 — this is its first reporting period, no
prior-year comparative exists. Source: ALP Industrial REIT Half-Year Report 2026 (unaudited,
period to 30-Jun-2026), alp.africa/half-year-report-2026.pdf, Trustee-certified 30-Jul-2026
(Co-operative Bank of Kenya).

| Property | Location | Class | GLA (sqm) | Occupancy | Valuation (USD) | Entry yield |
|---|---|---|---|---|---|---|
| ALP North Two | Tatu City, Kiambu | Grade A | 8,066 | 100% | 12,927,967 | 8.17% |
| Courtyard | Tilisi, Limuru | Grade B | 9,925 | 92% | 6,312,891 | 9.26% |
| Kyoga | Tilisi, Limuru | Grade B | 15,257 | 100% | 7,290,047 | 8.69% |
| **Total** | | | **33,248** | **98%** | **26,530,905** | |

Pipeline (not yet acquired at period end): ALP North Three, Tatu City SEZ. Balance sheet:
total assets $45,177,091; investment properties $26,530,905 (59% of assets); cash
$14,738,083; NAV (total unitholders' equity) $41,673,057; total liabilities $3,504,035 (all
current — trade payables + VAT provision, **zero borrowings**, 0% gearing); units in issue
39,950,000 → NAV/unit `[DISCLOSED-DERIVED]` **$1.0431**. Income statement (H1 2026): rental
399,737 + other 2,284 = operating income 402,021; less admin 31,962, fund opex 81,289,
one-off REIT set-up expenses 243,287 → operating profit 45,482; + finance income 187,605 →
net profit 233,087; EPU $0.0058. **No distributions yet** — first isn't due until after
year-end under the CMA's 4-month rule. Not found: no full audited annual report exists yet;
no secondary-market trading price found for a peer discount/premium figure.

Source: alp.africa/investor-relations, alp.africa/half-year-report-2026.pdf.

### TRIFIC Green USD I-REIT — no actuals exist yet (too newly listed)
Listed 23/29-Jun-2026 (sources disagree by a few days) — ~2 months before this research pass,
so **no annual or interim report has been published**. Only pre-listing marketing/prospectus
materials with forward *projections* were found — reporting this as a genuine, documented gap
rather than treating projections as disclosed actuals.

- Currency: **USD**, confirmed `[DISCLOSED]`.
- Seed/only asset: TRIFIC North Tower, Two Rivers SEZ, Gigiri, Nairobi — 174,694 sq ft GLA
  (16,213 sqm), green/EDGE-certified, fully let, anchor tenant Teleperformance, 87-year
  residual lease `[DISCLOSED]` — suntra.co.ke guideline PDF.
- Asset valuation: $37.3M platform value (asset itself cited elsewhere as $35.88M — the two
  sources disagree, flagged not reconciled). Offer size $29.8M pre-listing placement target.
- Annual rental income (asset-level, pre-listing estimate): $3.2M; avg rent $1.45/sq ft; 3.5%
  escalation `[DISCLOSED]` (prospectus estimate, not an audited actual).
- FY2027 *projections* (explicitly forward-looking, NOT actuals): gross operating income
  $3.2M, net distributable income $3.0M, DPU $0.08, payout >95%, yield >8%.
- Post-listing market data (22-Jul-2026): price $1.23/unit, market cap $45.9M, ~37.3M units
  `[DISCLOSED-DERIVED]` — afx.kwayisi.org/nse/trfc.html.
- **Not found anywhere**: NAV, NAV/unit, actual net profit, actual distributions, borrowings/
  LTV, units-in-issue register, any CMA-filed interim/annual report.

Recommendation: not sourceable as a real config instance yet — its first annual report
(likely FY2026, a partial listed period) probably won't publish until Q1-Q2 2027. Revisit
then, or check the CMA filing portal / NSE company-disclosures page directly.

Sources: suntra.co.ke/wp-content/uploads/2026/06/TRIFIC-GREEN-USD-I-REIT-GUIDELINE.pdf;
afx.kwayisi.org/nse/trfc.html; serrarigroup.com/trific-launches-kenyas-first-green-dollar-i-reit-at-sh4-8bn;
econews.co.ke/2026/05/25/trific-launches-kenyas-first-usd-denominated-green-i-reit-targeting-sh4-8bn.
(Note: ALP Industrial's own materials separately claim to be "Kenya's first" USD-denominated
I-REIT, chronologically plausible since ALP listed Mar-2026 vs. TRIFIC's Jun-2026 — flagged as
a marketing-claim discrepancy between the two REITs' own materials, not resolved here, and
irrelevant to either REIT's own figures above.)

### Sector cap rate for direct-capitalization valuation — no single authoritative figure exists
No formal "REIT cap rate" is published for Kenya; sources report rental/total-return yields by
segment instead. Real, dated findings:
- **Residential (general, Nairobi)**: 5.4% average rental yield, upper-mid suburbs
  (Westlands/Kilimani/Kileleshwa/Parklands) 7.1% total return `[DISCLOSED]` — Cytonn Nairobi
  Metropolitan Area Residential Report 2025 (cytonn.com/topicals/nairobi-metropolitan-area-32).
- 7.4% gross yield Nairobi suburbs (steady), 5.3% satellite towns `[DISCLOSED]` — Knight Frank
  Kenya Market Update, H1 2025.
- 7.4% overall Nairobi rental yield, Q4 2025, "highest since 2007" `[DISCLOSED]` — HassConsult
  Q4 2025 data, via Cytonn/afriqahome.com.
- Budget nodes (Pipeline, Kahawa West, Ruaka): 8-12% gross yields `[DISCLOSED]`.
- **Office (prime)**: 8-9% yields, stable `[DISCLOSED]` — Knight Frank Kenya Market Update, H1
  2025; occupancy 80.3% as of March 2026.
- **Student housing** (Acorn's own segment) — stale: 7.4% average rental yield vs. 7.3%
  mixed-use, 5.0% residential `[DISCLOSED]` but dated 2020-03-08 (Cytonn) — predates Acorn's
  current portfolio scale and the 2025/2026 rate-easing cycle; **not usable as current**.
- **ILAM Fahari's own independently-valued yields** (see Note 11 table above) are the single
  best-sourced, most-current formal cap-rate-equivalent found: retail 13.0% term / 9.0%
  reversionary / 13.0% discount; office & light industrial 12.5% / 9.0% / 12.5% (both FY2025).
- **ALP Industrial's own disclosed entry yields** (industrial/logistics): 8.17%-9.26%
  `[DISCLOSED]` (see table above).

**Cross-check against Acorn's own `cap_rate` input** (5.47%, `[DISCLOSED-DERIVED]` in
`config.py`, from H1 2025 NOI ÷ investment property fair value): sits comfortably within the
general Nairobi residential range found above (5.4%-7.4%), a reasonable validation for a
student-housing REIT even though no segment-identical published benchmark exists — no change
made to the config value, this is documentation/cross-check only.

Sources: cytonn.com/topicals/nairobi-metropolitan-area-32;
knightfrank.com/research/report-library/kenya-market-update-12364.aspx;
afriqahome.com/guides/kenya-real-estate-2026; cytonnreport.com/topicals/student-housing-market-1
(2020, stale); cytonnreport.com/research/review-of-real-estate-investments-trusts-reits-in-kenya-and-cytonn-weekly-052026-1.

## 2026-09-03 — Two-tier seed/stabilized occupancy model (per-property page-11 data)

User proposed enhancing the rental-income schedule using per-property detail from the ASA
I-REIT semi-annual report's own p.11 "Portfolio Update" (rooms/beds/operations-start/
acquisition-date per property) and modeling occupancy "by regression." Pulled the actual PDF
(`acornholdingsafrica.com/wp-content/uploads/2025/08/ASA-I-REIT-2025-Semi-Annual-Report.pdf`)
directly and read every page mentioning occupancy or the 7 properties, including rendering
p.12's occupancy-trend chart as an image to check for embedded data labels a text-only
extraction might miss.

**What's actually disclosed**: p.11 gives real per-property rooms/beds/location/operations-
start/acquisition-date `[DISCLOSED]` — now in `config.py`'s `PROPERTIES` (`operations_start`
field, previously missing). **No per-property or continuous occupancy series is disclosed
anywhere** — p.12 ("Portfolio Occupancy Trend") gives only a portfolio-blended monthly chart
(confirmed via direct image inspection: two lines, H1-2025 vs H1-2024, no per-property split,
no data labels beyond the two H1-average callouts already known) plus a **qualitative
two-group split**: "seed" assets Acorn itself names as underperforming — Jogoo Road (worst;
"absence of an anchor institution" + "accessibility constraints due to an incomplete access
road"), Ruaraka and Parklands (undisclosed dips) — versus "stabilized typical assets" (the
other 4), disclosed at 93% H1-2025 / 92% H1-2024 occupancy `[DISCLOSED]`. A literal regression
isn't fittable from this — there's no multi-point occupancy series per property to fit a curve
through, only one clean tier-level number (the stabilized group) plus qualitative commentary
for the other.

**What is legitimately derivable**: since portfolio-blended occupancy = the bed-weighted
average of both tiers, and both the portfolio-blended and stabilized-tier figures are
disclosed for two periods, the seed tier's occupancy for those same two periods is solvable
as the residual — `[DISCLOSED-DERIVED]`, not fabricated:
- Seed beds 1,578 (Jogoo Road 502 + Ruaraka 543 + Parklands 533); stabilized beds 2,888
  (Wilsonview 728 + Aberdare Heights I 697 + Hurlingham 834 + Aberdare Heights II 629);
  total 4,466 (matches the disclosed portfolio bed count).
- H1-2025: (4,466 × 81% − 2,888 × 93%) / 1,578 = **59.0%**.
- H1-2024: (4,466 × 88% − 2,888 × 92%) / 1,578 = **80.7%** (using the H1-2024 comparatives
  disclosed on the same p.12 chart, now in `config.py` as `occupancy_portfolio_h1_2024` /
  `occupancy_stabilized_h1_2024`).

This gives a real, second data point showing the seed tier's occupancy **declined** from
80.7% to 59.0% year-on-year — consistent with Jogoo Road's disclosed anchor-tenant loss and
access-road disruption emerging/worsening between the two periods, and importantly **not** a
"new property still ramping up" story.

**Important correction to my own initial framing**: I originally assumed the seed/stabilized
split would track property age (newer properties still maturing toward stabilized occupancy).
The actual operations-start dates disprove this cleanly: Jogoo Road (Aug-2017, the *oldest*
property) and Ruaraka (Jan-2018, 2nd oldest) are both "seed", while Aberdare Heights II
(Apr-2022, the *newest* property) is already "stabilized". The seed/stabilized split is
Acorn's own qualitative *operational* categorization (anchor-tenant loss, access-road
construction, sales execution gaps) — not a maturity curve. A regression of occupancy against
property age would have been actively misleading here, which is why one wasn't built.

**Implementation**: `config.py`'s `PROPERTIES` entries now carry a `tier` field ("seed" /
"stabilized"); `reit_calculations.py` adds `compute_tier_beds()`, `compute_seed_occupancy()`
(generic back-solve), and `compute_seed_occupancy_h1_2024/2025()`, and `build_rental_income_noi()`
now models each tier separately (stabilized held flat at the scenario-flexed target, seed
glides toward it over `occupancy_recovery_years`) before bed-weighting them back into one
portfolio figure. The rendered Excel workbook mirrors this as three live-formula Model-sheet
rows (Seed tier / Stabilized tier / blended), not just a Python-side change — cross-verified
with the `formulas` package (a real Excel-formula evaluator) that the rendered workbook
evaluates to the exact same numbers as the Python ground truth across Base/Best/Worst
scenarios, and that the Master Check still reads OK for Balance Sheet/LTV/Income-Producing in
all 24 year×scenario combinations. That verification pass also caught a real latent bug (in
the *prior* single-tier design too, not introduced by this change): the scenario-flexed
occupancy target was never actually capped at 100% in the rendered Excel formulas (only Python
capped it), so an extreme Best-case could show occupancy above 100% of beds — fixed by capping
the target reference in both tiers' formulas.

Base-case blended occupancy numbers are numerically **unchanged** from the prior single-glide
design (85%/89%/93% for 2026-2028) — this is a mathematical necessity, not a coincidence: a
bed-weighted blend of "flat at target" and "linear glide to the same target" is itself a
linear glide from the same starting point to the same target, regardless of the tier split
or back-solved seed value chosen. The real gains are (1) correct, disclosure-traceable
provenance instead of one unexplained blended number, (2) more realistic Best/Worst scenario
behavior — the ceiling effect now applies per-tier instead of only once the whole portfolio
has fully converged, and (3) the back-solved seed occupancy (59.0% H1-2025, declining from
80.7% H1-2024) is now visible as its own figure rather than hidden inside a blend.

**Also fixed while here**: the Model sheet's actual-year occupancy display for 2024 was a
prior unsourced `0.85` — replaced with the disclosed `0.88` (portfolio-blended H1-2024). 2023's
`0.78` has no disclosed source found in any research pass to date and is left as an
unexplained pre-existing placeholder, flagged for future sourcing rather than silently
"fixed" with an invented number.

Source: `ASA I-REIT 2025 Semi-Annual Report`, pp.11-12 ("Portfolio Update" / "Portfolio
Occupancy Trend"), same document already cited above.
