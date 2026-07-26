# Research Output — Family Bank Kenya

Calibration figures for the bank financial model generator (see root `BLUEPRINT.md`).
Primary source is the repo's own `data/` folder. Every figure below carries a `source` and
`accessed` field. This is a working research log, not the final Assumptions sheet — it
feeds `config.py` once that's written (Phase 4).

## Update 2026-07-06 — real FY2025 data, `data/` reorganized, 5 broken PDFs fixed

`data/` was reorganized into per-bank subfolders (`family_bank/`, `absa/`, `co-op/`, `dtb/`,
`equity/`, `i&m/`, `kcb/`, `ncba/`, `scb/`, `stanbic/`), each with re-downloaded, readable
annual reports (the 4 broken Family Bank PDFs from the original research pass are fixed —
`data/family_bank/` now has all 5 years 2021-2025 readable). The forecast basis changes
accordingly: **opening balance sheet moves from FY2023 to FY2025** (YEARS becomes
2026-2030). All FY2025 figures below are **[DISCLOSED]**, straight from
`data/family_bank/Integrated-Report-and-Financial-Statements-2025.pdf`, accessed 2026-07-06.

### Family Bank FY2025 — full balance sheet (Consolidated, Kshs '000)

| | FY2025 | FY2024 |
|---|---:|---:|
| Cash and balances with CBK | 9,801,482 | 12,153,067 |
| Balances due from banking institutions | 7,874,262 | 2,858,176 |
| Government securities — amortised cost | 39,704,276 | 22,192,287 |
| Government securities — FVOCI | 34,330,870 | 28,806,539 |
| Other assets | 3,389,193 | 2,710,862 |
| Loans and advances to customers (net) | 105,898,912 | 92,908,565 |
| Investment properties | 70,600 | 32,500 |
| Property and equipment | 2,401,037 | 2,366,038 |
| Intangible assets | 765,015 | 469,744 |
| Right of use assets | 1,009,320 | 685,034 |
| Prepaid operating leases | 114,006 | 118,643 |
| Deferred income tax | 3,315,050 | 2,879,005 |
| **Total assets** | **208,688,568** | **168,504,562** |
| Customer deposits | 151,878,945 | 126,471,079 |
| Balances due to banking institutions | 561,679 | 7,125,532 |
| Accruals and other provisions | 2,015,038 | 2,101,088 |
| Other liabilities | 5,741,759 | 2,073,325 |
| Borrowings | 13,911,503 | 7,491,175 |
| Lease liabilities | 1,184,732 | 852,949 |
| **Total liabilities** | **176,066,082** | **146,115,148** |
| Share capital | 1,662,655 | 1,305,195 |
| Share premium | 10,944,549 | 6,118,846 |
| Revaluation surplus | 506,423 | 278,424 |
| Fair value reserve | 1,305,334 | 752,161 |
| Retained earnings | 13,423,447 | 9,733,792 |
| Statutory reserve | 2,551,376 | 3,092,496 |
| Proposed dividends | 2,228,702 | 1,108,500 |
| **Total shareholders' funds** | **32,622,486** | **22,389,414** |

### Family Bank FY2025 — income statement (Consolidated, Kshs '000)

Interest income 25,169,995; interest expense (9,044,187); **NII 16,125,808**; net fees &
commission 2,068,571; investment income 1,061,246; net trading income 330,913; other income
442,236; **operating income 20,028,774**; operating expenses (11,135,575); credit
impairment losses (2,562,847); **PBT 6,330,352**; tax (952,199); **PAT 5,378,153**; EPS 3.93.

### Family Bank FY2025 — IFRS 9 stage table by product (Kshs '000), p.199

| | Term loans | Mortgage | Overdraft & credit cards | Total | Off-BS |
|---|---:|---:|---:|---:|---:|
| Gross — Stage 1 | 74,732,268 | 12,946,847 | 1,506,935 | 89,186,050 | 3,094,008 |
| Gross — Stage 2 | 8,355,106 | 1,580,111 | 461,631 | 10,396,848 | — |
| Gross — Stage 3 | 12,303,290 | 1,395,340 | 638,333 | 14,336,963 | — |
| **Gross total** | 95,390,664 | 15,922,298 | 2,606,899 | **113,919,861** | 3,094,008 |
| ECL — Stage 1 | 805,781 | 13,487 | 5,971 | 825,239 | 4,972 |
| ECL — Stage 2 | 672,013 | 44,337 | 27,542 | 743,892 | — |
| ECL — Stage 3 | 5,992,192 | 202,602 | 257,024 | 6,451,818 | — |
| **ECL total** | 7,469,986 | 260,426 | 290,537 | **8,020,949** | 4,972 |
| Net loans | 87,920,678 | 15,661,872 | 2,316,362 | **105,898,912** | 3,089,036 |

Derived loss rates (disclosed-derived, same method as the FY2023 pass): Stage 1 — Term
0.845%/1.078%, Mortgage 0.104%/... ; recompute exactly in `config.py` from these figures.

### Family Bank FY2025 — key ratios (p.41), FY2024 vs FY2025

NIM 7.6%→8.6%; Cost-to-Income 74.8%→69.4%; Core Capital/Deposits 12.0%→16.0%; Core
Capital/RWA 13.5%→16.9%; Total Capital/RWA 17.8%→19.6%; Liquidity 43.90%→60.9%; Book Value/
share 17.15→19.62; EPS 2.65→3.93; Dividend Yield 6.1%→6.7%; ROAE 15.5%→16.5%; ROA 2.1%→2.6%.

Sector context (p.39, p.188-189): industry CAR 20.4% (vs 14.5% min), industry liquidity
58.4%; new core-capital minimum rising to Shs 10bn by 2029 (Business Laws Amendment Act
2024); 2026 GDP growth forecast 4.5% (IMF) to 5.3% (Treasury); inflation ~4-5%; CBK
benchmark rate ~9%; industry NPL ~16-17%; pre-2027 election uncertainty flagged as a risk
factor informing the macro overlay.

### Peer bank real data (replacing placeholders where found)

- **NCBA** (`data/ncba/NCBA-Group-Plc-Annual-2025-Integrated-Report.pdf`, p.32,
  **[DISCLOSED]**): PAT FY25 23,394M; Market Cap KES 138bn; EPS 14.2; DPS 7.10;
  **P/B 1.2x (directly disclosed)** — trend 0.7x (FY23) → 0.8x (FY24) → 1.2x (FY25); ROAE
  19.7%; Cost-to-Income 52.3%; NIM 7.1%; NPL 10.2%; ROAA 3.4%.
- **I&M Group** (`data/i&m/2025-INTEGRATED-REPORT-TPALAZEDIT8.pdf`, p.120, **[DISCLOSED]**):
  EPS 10.8; DPS 3.75; Book Value Per Share KES 66; share price ~42.50 (chart, Jan 2026) →
  **implied P/B ≈ 0.64x [DISCLOSED-DERIVED]**.
- **Co-operative Bank** (`data/co-op/2025-Co-op-Bank-Integrated-Report-Web.pdf`, p.17,
  **[DISCLOSED]**): Market Cap KES 140.7bn; ROA 3.8%; ROE 19.1%; Dividends KES 14.7bn; Loans
  KES 421bn. Book value of equity not found in the extracted pages (searched); P/B not yet
  computable — real market cap is usable directly if the valuation cross-check is built
  around market cap rather than P/B for this one.
- **Absa, DTB, Equity, KCB, SCB (StanChart), Stanbic**: searched each bank's FY2025 report
  for "book value per share" / "price to book" / "market capitalisation" / "share price" —
  no direct textual hits (likely presented as infographic images, not extractable as text).
  **Still `[PLACEHOLDER]`** — EPS/ROAE/payout from the MTN memorandum peer table remain the
  basis for these 5; flagged honestly rather than fabricated.

## Update 2026-07-06 (cont.) — FY2023 full BS/IS + FY2023-2025 Cash Flow Statements

For the historical-actuals rework (3 actual years 2023-2025 on the Model sheet). All
**[DISCLOSED]**, sourced from `data/family_bank/Integrated-Report-and-Financial-Statements-2024.pdf`
(FY2023 comparative columns, p.153/156) and `-2025.pdf` (FY2024 restated comparative, p.168),
accessed 2026-07-06.

### FY2023 full balance sheet (Consolidated, Kshs '000) — closes the earlier gap

Cash and balances with CBK 9,250,646; balances due from banking institutions 2,646,725;
government securities amortised cost 24,296,347 + FVOCI 10,529,403; other assets 2,496,276;
loans and advances (net) 86,921,359; investment properties 28,600; PP&E 2,487,557;
intangible assets 543,317; ROU assets 760,152; prepaid leases 123,280; deferred tax
2,274,779; **total assets 142,406,925**. Customer deposits 102,594,430; short-term CBK
borrowings 3,000,000; balances due to banks 4,384,574; accruals & other provisions
1,112,054; other liabilities 2,247,914; borrowings 11,240,600; lease liabilities 956,570;
**total liabilities 125,536,142**. Share capital 1,287,108; share premium 5,874,662;
revaluation surplus 278,424; fair value reserve (1,766,320); retained earnings 7,879,305;
statutory reserve 2,594,636; proposed dividends 722,968; **total shareholders' funds
16,870,783**. Ties out exactly and reconciles with the FY2023 aggregate figures already
in hand (142.4bn assets, 102.6bn deposits, 16.9bn capital).

### Cash Flow Statements — FY2023, FY2024 (as originally reported and restated), FY2025

| (Consolidated, Kshs '000) | FY2023 | FY2024 (orig.) | FY2024 (restated) | FY2025 |
|---|---:|---:|---:|---:|
| Net cash from operating activities | (2,588,532) | 7,835,665 | 8,361,768 | 1,088,142 |
| Net cash from investing activities | (1,124,298) | (493,693) | (493,693)* | (803,402) |
| Net cash from financing activities | 2,485,810 | (7,952,861) | (7,495,162) | 8,943,614 |
| Cash & equivalents, end of year | 3,175,178 | 2,564,289 | 7,885,711 | 17,114,065 |

*FY2024 figures were restated in the FY2025 report (e.g. operating CF 7,835,665 →
8,361,768) — a meaningful restatement between reports. **Using the FY2025 report's
restated FY2024 figures** (more recent/final) rather than the FY2024 report's original
figures, for internal consistency with the FY2025 actual column. Note the CF statement's
"cash and cash equivalents" is a narrower/different definition than the balance sheet's
"cash and balances with CBK" + "balances due from banks" combination used elsewhere in
this model (`OPENING_CASH`) — a known, documented simplification, not reconciled exactly.

### Beta

No market-data API available to compute a true regression beta (needs a historical price
series + market index returns). Damodaran's emerging-markets industry beta dataset exists
(`ctryprem`-adjacent files at stern.nyu.edu) but requires parsing an `.xls` file not cleanly
fetchable with the tools here. **Using beta = 1.0 as a reasoned neutral proxy**
**[PLACEHOLDER]** — frontier-market bank equity betas typically run 0.8-1.1x; 1.0 is the
midpoint, not a sourced figure. Flagged clearly in the Assumptions sheet.

## Data source status (`data/`)

| File | Status | Notes |
|---|---|---|
| `Integrated-Report-and-Financial-Statements-2023.pdf` | **Usable** (204pg) | Full IFRS 9 note with product-level stage disclosure |
| `ke-fmly-2026-ps-00.pdf` | **Usable** (276pg) | MTN Information Memorandum 2026, covers FY2021-2025; peer comparables; sector outlook |
| `FBL_LISTING_ABRIDGED_NEWSPAPER_FINAL-1.pdf` | **Usable** (16pg) | Thin content; has CAR/liquidity/NPL mentions p.14-15 |
| `Integrated-Report-and-Financial-Statements-2024.pdf` | **Broken — truncated download.** File declares a linearized length of 27,195,832 bytes but is only 589,500 bytes on disk (~2% of the real file). Needs re-downloading from source; not repairable. |
| `Integrated-Report-and-Financial-Statements-2025.pdf` | **Broken.** Correct total byte count but the PDF Catalog is missing its `/Pages` reference even after full `pikepdf` recovery — consistent with a partial export from a page-flip/streaming viewer rather than a standard full download. Tried `pypdf`, `pdfplumber`, `PyMuPDF`, `pikepdf` recovery — all fail identically. Needs a clean re-export/re-download. |
| `Integrated-Report-Financial-Statements-2021-1.pdf` | **Broken.** Same failure mode as 2025. |
| `Integrated-Report-Financial-Statements-2022.pdf` | **Broken**, worse — `pikepdf` recovery can't even find a trailer dictionary. |
| `Family-Bank_MTN-_Information-Memorandum.pdf` | **Broken.** Same failure mode as 2025/2021 (missing `/Pages` in Catalog). Note: distinct from `ke-fmly-2026-ps-00.pdf`, which is also an MTN Information Memorandum (2026) and *is* readable — likely supersedes this one. |

**Action needed from the user**: re-download/re-export clean copies of the 2024 and 2025
annual reports, the 2021 and 2022 annual reports, and the (older) MTN memorandum if it has
content not already covered by `ke-fmly-2026-ps-00.pdf`. Direct "Download PDF" from the
source system, not a page-flip viewer export, if that's how these were originally saved.

## IFRS 9 loan staging — real disclosed figures (2023 annual report, p.144-145)

Family Bank discloses gross loans/ECL **by product type** (Term loans, Mortgage,
Overdraft & credit cards), not by customer segment (Retail/MSME/Corporate) as the blueprint
initially assumed — update the config's segmentation to match actual disclosure.

**FY2023 (Kshs '000)**, *source: Integrated Report & Financial Statements 2023, p.144-145,
accessed 2026-07-05*:

| | Term loans | Mortgage | Overdraft & credit cards | Total | Off-BS |
|---|---:|---:|---:|---:|---:|
| Gross — Stage 1 | 61,346,247 | 10,183,039 | 2,053,586 | 73,582,872 | 3,718,240 |
| Gross — Stage 2 | 3,467,725 | 706,859 | 411,914 | 4,586,498 | — |
| Gross — Stage 3 | 11,130,623 | 2,156,329 | 1,122,155 | 14,409,107 | — |
| **Gross total** | 75,944,595 | 13,046,227 | 3,587,655 | **92,578,477** | 3,718,240 |
| ECL — Stage 1 | 856,406 | 14,645 | 17,823 | 888,874 | 11,561 |
| ECL — Stage 2 | 337,131 | 30,865 | 26,920 | 394,916 | — |
| ECL — Stage 3 | 3,807,821 | 119,874 | 445,633 | 4,373,328 | — |
| **ECL total** | 5,001,358 | 165,384 | 490,376 | **5,657,118** | 11,561 |
| Net loans | 70,943,237 | 12,880,843 | 3,097,279 | **86,921,359** | 3,706,679 |

**FY2022 comparative** (same source, p.145): gross total 85,807,273; Stage 3 gross
12,431,240; ECL total 4,426,763; Stage 3 ECL 3,090,964; net loans 81,380,510.

**Derived coverage ratios (calibration anchors, disclosed-fact tier)**:
- Total coverage ratio 2023: 5,657,118 / 92,578,477 = **6.11%**
- Stage 3 (NPL) coverage ratio 2023: 4,373,328 / 14,409,107 = **30.35%**
- NPL ratio (Stage 3 / gross) 2023: 14,409,107 / 92,578,477 = **15.57%**
- Stage 1 "12-month ECL rate" proxy, Term loans 2023: 856,406 / 61,346,247 = **1.40%** —
  this is a *real disclosed* Stage 1 coverage rate, usable directly instead of a Basel
  proxy for the Term Loans product line.

Note the 2023 commentary (p.71): "aggressive provisions on the loan book, which saw a 28%
increment in loan loss provisions" — a real data point for the buy-side
quality-of-earnings/reversion-to-norm check in `BLUEPRINT.md`.

## Regulatory capital (Family Bank's own disclosure)

*Source: Integrated Report & Financial Statements 2023, p.167, and MTN Information
Memorandum 2026 (`ke-fmly-2026-ps-00.pdf`), p.200, accessed 2026-07-05*:

- Core capital / RWA ≥ **10.5%**
- Core capital / total deposit liabilities ≥ **8%**
- Total capital / RWA ≥ **14.5%**
- Minimum core capital (absolute): Shs 1bn (FY2021-2024) → Shs 3bn (FY2025) → **Shs 5bn by
  31 Dec 2026** (confirmed directly in the MTN memorandum's 2026 outlook section, p.66,
  matching the secondary web-search figure found during planning) → Shs 10bn by end 2029
  (per web search during planning; not yet directly confirmed in a primary document).
- Tier 1: ordinary share capital, disclosed reserves, retained earnings, 50% unaudited
  after-tax profit, less intangibles/goodwill/investments in subsidiaries.
- Tier 2: 25% CBK-approved revaluation surplus, subordinated debt, other CBK-approved
  hybrid instruments.
- Statutory liquidity ratio minimum: **20%** (confirmed, matches secondary source).

## Family Bank actuals — multi-year trend (real, disclosed)

| | FY2022 | FY2023 | FY2025 |
|---|---:|---:|---:|
| Total assets (KES bn) | — | 142.3 (+11%) | 208.7 (+23.9%) |
| Net loans (KES bn) | 81.4 | 86.9 (+6.8%) | 105.9 (+14.0%) |
| Customer deposits (KES bn) | — | 102.6 (+15.4%) | 151.88 (+20.1%) |
| Government securities (KES bn) | — | 34.8 (+35.2%) | — |
| Net interest income (KES bn) | — | — (+6.3%) | 15.63 (+46.1%) |
| Total capital (KES bn) | — | 16.9 (+4.7%) | — |
| Total CAR | — | 16.9% | 19.6% |
| Liquidity ratio | — | 38.7% | — |
| PAT (KES bn) | — | 2.5 (+13.3%) | 5.38 (+55.4%) |

*Sources: 2023 figures from Integrated Report & Financial Statements 2023, p.71 (accessed
2026-07-05); FY2025 figures from secondary web sources (familybank.co.ke, Kenyan
Wallstreet, TechCabal) gathered during planning — treat as cross-check pending direct
extraction from the (currently broken) FY2025 annual report. **FY2024 is a genuine gap**
until that annual report PDF is replaced.*

## Peer bank comparables (for the P/B-ROE regression and P/E cross-check)

*Source: MTN Information Memorandum 2026 (`ke-fmly-2026-ps-00.pdf`), p.65, accessed
2026-07-05. EPS in Kshs, ROAE/payout/DPS growth in %, DPS in Kshs:*

| Bank | EPS FY24 | EPS FY25 | EPS % chg | ROAE FY24 | ROAE FY25 | Payout FY25 | DPS FY24 | DPS FY25 | Div % growth |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Absa | 3.8 | 4.2 | 9.7% | 27.0% | 24.7% | 48.6% | 1.75 | 2.05 | 17.1% |
| Co-op Bank | 4.3 | 5.0 | 16.4% | 19.7% | 19.1% | 49.6% | 1.50 | 2.50 | 66.7% |
| DTB | 27.3 | 33.7 | 23.1% | 9.8% | 10.3% | 26.7% | 7.00 | 9.00 | 28.6% |
| Equity Group | 12.3 | 19.1 | 54.5% | 21.1% | 26.5% | 30.2% | 4.25 | 5.75 | 35.3% |
| I&M Group | 8.9 | 10.8 | 21.2% | 16.2% | 18.0% | 34.8% | 3.00 | 3.75 | 25.0% |
| KCB Group | 18.7 | 20.8 | 11.2% | 24.6% | 22.5% | 33.7% | 3.00 | 7.00 | 133.3% |
| NCBA | 13.3 | 14.2 | 7.0% | 21.2% | 19.7% | 50.0% | 5.50 | 7.10 | 29.1% |
| Stanbic Holdings | 34.7 | 34.7 | 0.0% | 19.3% | 18.0% | 64.4% | 20.83 | 22.35 | 7.3% |
| StanChart | 52.7 | 32.5 | -38.3% | 30.1% | 18.0% | 95.5% | 45.00 | 31.00 | -31.1% |

**Still needed for the multiples cross-check**: market cap and book value of equity per
peer (to compute actual P/B and P/E — this table gives EPS/ROAE/DPS but not share price or
book value directly). Pull from NSE market data or the peers' own published financials.

## Sector/macro outlook (forward-looking, for the IFRS 9 macro overlay)

*Source: MTN Information Memorandum 2026, p.65-66, accessed 2026-07-05*:

- Industry gross NPL ratio **peaked at 17.6% in mid-2025**, moderating since as government
  settles pending bills — a real through-the-cycle sector benchmark, not just Family
  Bank's own trend.
- NIMs expected to face **modest compression in 2026** as loan books reprice down following
  2025 CBR cuts and government-security yields moderate — informs the Base Case NIM
  trajectory (should not be flat/rising).
- **Risk-Based Credit Pricing Model (RBCPM)** full implementation by 28 Feb 2026 for all
  variable-rate loans — a live regulatory change relevant to loan yield assumptions; note
  in the Assumptions sheet.
- Capital-adequacy discipline (Shs 5bn core capital minimum by 31 Dec 2026) expected to
  accelerate sector consolidation; several small/mid-tier banks entered 2026 with capital
  shortfalls.
- Sector trending toward "volume-over-margin": digital-channel/fee income growth, branch
  rationalization, cloud migration — informs opex trajectory assumptions (cost-to-income
  should trend down, not flat).

## Update 2026-07-06 (later) — Regulatory capital bridge & sector concentration detail

Researched for the "regulatory capital bridge" and "CBK compliance detail" backlog
follow-ups. Extracted full text from `Integrated-Report-and-Financial-Statements-2023.pdf`,
`...-2024.pdf`, `...-2025.pdf`, and `information_memorandum_2026.pdf`.

### Regulatory Capital Adequacy note (Family Bank's own Capital Management note)

No Basel-style Credit/Market/Operational RWA split exists anywhere in these four
documents — only one aggregate RWA figure per year. Full Tier 1/Tier 2 build-up, all
[DISCLOSED], KES '000:

**FY2023** (Integrated Report & Financial Statements 2023, p.168): Share capital
1,287,108; Share premium 5,874,662; Retained earnings 7,410,682 → Total Tier 1
14,572,452. Revaluation reserve (25%) 69,606; Term subordinated debt 3,200,000;
Statutory reserve 2,594,636 → Total Tier 2 5,864,242. Total regulatory capital
20,436,694. RWA 108,176,948. Core/Total CAR: 13.47%/18.89%.

**FY2024** (originally reported — Integrated Report & Financial Statements 2024, p.219):
Share capital 1,305,195; Share premium 6,118,846; Retained earnings 9,066,319 → Total
Tier 1 16,490,360 (no deferred-tax deduction line in this presentation). Tier 2:
Revaluation 69,606; Sub debt 1,600,000; Statutory reserve 3,092,496 → 4,762,102. Total
regulatory capital 21,252,462. RWA 112,558,659. Core/Total CAR: 14.65%/18.88%.

**FY2024 — RESTATED** (Integrated Report & Financial Statements 2025, p.238, used in
`config.py` per this project's "prefer the more recent restatement" convention, same as
the Cash Flow Statement fix): adds a Deferred Tax deduction of (1,266,898) → Total Tier 1
15,223,462. Tier 2 unchanged at 4,762,102. Total regulatory capital 19,985,564. RWA
unchanged at 112,558,659. Core/Total CAR: 13.52%/17.76%.

**FY2025** (Integrated Report & Financial Statements 2025, p.238): Share capital
1,662,655; Share premium 10,944,549; Retained earnings 12,908,471; Deferred tax
(1,111,321) → Total Tier 1 24,404,354. Tier 2: Revaluation 0; Sub debt 2,090,500;
Statutory reserve 1,808,796 → 3,899,296. Total regulatory capital 28,303,650. RWA
144,703,676. Core/Total CAR: 16.87%/19.56% (matches the headline figures already in this
file's earlier sections exactly).

CBK minimums, Tier 1/Tier 2 definitions (Integrated Report 2023 p.167, 2024 p.218, 2025
p.237, Information Memorandum 2026 p.200) — unchanged from what's already documented
above; Tier 1 = ordinary share capital + non-cumulative irredeemable preference shares +
share premium + retained earnings + 50% unaudited after-tax profit, less investments in
subsidiaries/other institutions' equity/intangibles (excl. software)/goodwill; Tier 2 =
25% of CBK-approved revaluation surplus + subordinated debt + hybrid instruments/other
CBK-approved instruments.

**IM 5-year table caveat**: the Information Memorandum 2026 (p.201) reproduces a
2021-2025 capital table, but pdfplumber extraction shows misaligned cells for the 2021
and 2023 columns on individual line items (only the Total Tier 1 lines for those years
match the standalone annual reports) — the standalone Integrated Reports above are the
authoritative source for FY2023-FY2025.

### CBK concentration/exposure limits

**Single-borrower/large-exposure limit: not disclosed.** Searched all four documents for
"single borrower", "large exposure", "single obligor", "25% of core capital" — none
found. Only generic risk-policy narrative exists ("The Group structures the level of
credit risk it undertakes by placing limits on amounts of risk accepted in relation to
one borrower or a group of borrowers" — Integrated Report 2025, p.195). Family Bank does
not disclose its own largest exposures or an internal single-obligor limit figure.
Decided (per user confirmation): don't fabricate a check against a number that doesn't
exist in the disclosure — build sector concentration only.

**Sector concentration — real disclosed loan-by-sector tables** (advances to customers
before impairment, KES '000). Family Bank changed its classification scheme between
FY2023 and FY2024/2025:

FY2023/FY2024, 7-category scheme (Integrated Report & Financial Statements 2024, p.201):
Manufacturing 1,164,055/4,489,945; Wholesale and retail 35,411,499/34,338,087; Transport
and communication 4,623,765/5,024,269; Agriculture 5,949,684/5,796,310; Business services
3,305,282/3,321,014; Building and construction 3,777,774/4,145,574; Other
32,689,300/35,793,366. Totals: 86,921,359 (FY2023) / 92,908,565 (FY2024).

FY2024 (restated)/FY2025, 10-category scheme (Integrated Report & Financial Statements
2025, p.214, "4.1.4 Concentration of risk"): Agriculture 5,018,959/8,162,107; Building and
Construction 3,955,368/4,966,298; Energy and water 1,122,413/1,260,169; Finance &
Insurance Services 3,292,526/3,371,756; Manufacturing 4,463,402/5,764,765;
Personal/Household 26,080,949/30,446,850; Real Estate 10,858,692/10,577,623; Tourism,
restaurant and Hotels 2,422,828/2,683,742; Trade 31,349,652/33,914,447; Transport and
Communication 4,343,776/4,751,155. Totals: 92,908,565 (FY2024) / 105,898,912 (FY2025) —
both tie to the disclosed net loan balances already in this file.

**Related-party/insider lending** (Integrated Report 2025, p.272-273; Information
Memorandum 2026, p.84): director/associate loans closing balance FY2025 5,652,618 (KES
'000); staff loans closing balance 1,783,337; IM states Family Bank asserts general
compliance with Banking Act insider-lending prohibitions but doesn't disclose the
specific percentage limit or its utilization against it.

## Update 2026-07-06 (later still) — Bank (standalone) vs Consolidated (Group) figures

Discovered that every actual figure in `config.py` up to this point had been sourced from
the **Consolidated (Group)** column of Family Bank's annual reports, not the **Bank
(standalone)** column — both are presented side-by-side for the Balance Sheet, Income
Statement, and Cash Flow Statement in all three years (FY2023/FY2024/FY2025 Integrated
Reports). Per the modeling principle that a bank within a group should be modeled on its
own standalone data, every actual figure was re-sourced to the Bank column. Full detail
(citations, page numbers) already written into `config.py`'s `ACTUALS`/`REGULATORY_CAPITAL`
comments; summarized here for the research trail.

**Sources**: `Integrated-Report-and-Financial-Statements-2023.pdf` (BS/IS p.114-115, CF
p.118, notes p.168-170), `...-2024.pdf` (BS p.153, IS p.152, CF p.156, notes p.220-222,
239), `...-2025.pdf` (BS/IS p.164-165, CF p.168, notes p.239-243, 266-267).

**What ties exactly between Bank and Consolidated** (no correction needed): the entire
loan book (gross/ECL by stage — subsidiaries aren't a lending business), Government
Securities at FVOCI, `REGULATORY_CAPITAL`'s Tier 1/Tier 2 build-up (the Capital Management
note is inherently solo/Bank-basis under CBK regulation), Share Capital + Share Premium,
Cash and Balances with CBK + Due from Banking Institutions, Interest Income (2023/2024)
and Impairment/Provisions (all 3 years).

**What required correction** (Bank vs Consolidated, all real, all cited in `config.py`):
Government Securities at Amortised Cost (small, ~KES 20m/year); the entire "Other Assets"
bucket (Current Tax Asset, Investment Properties, Intangibles, ROU Assets, Prepaid
Leases, Deferred Tax Asset, Other Assets residual, and a genuine Bank-only "Investment in
Subsidiaries" line that doesn't exist on a Consolidated basis at all); the entire "Other
Liabilities" bucket (Due to Banks, Short-Term CBK Borrowings, Accruals & Provisions,
Borrowings, Lease Liabilities, Current Tax Liability); Customer Deposits; the equity
reserve lines (Revaluation Surplus, Fair Value Reserve, Retained Earnings, Statutory
Reserve, Proposed Dividends — previously blended into one bucket, now shown separately);
Interest Expense (all 3 years); Non-Interest Income's "other income" sub-component (Bank
excludes Group-only brokerage commission); Operating Expenses; PBT/Tax/PAT; and the
Operating/Investing Cash Flow split for FY2024/FY2025 (Financing CF and ending cash were
already correct — apparently sourced from a Bank-labeled table in the original pass even
though the Balance Sheet wasn't).

**Two real restatement quirks found, both driven by Family Bank broadening its "cash and
cash equivalents" definition across report vintages** (same underlying pattern as the
Consolidated-basis restatement found earlier this project, now confirmed on a Bank basis
too — per the established "prefer the most recent restatement" convention):
- **FY2023**: the FY2023 report's own ending cash (2,639,119 KES'000) differs from the
  FY2024 report's restated FY2023 comparative (3,175,178) — the FY2024 report adds
  "Unrestricted balances with CBK" (536,059) to the cash-equivalents definition. Used the
  restated (FY2024 report) figure, consistent with the Consolidated-basis handling
  already in this file.
- **FY2024** (larger, ~3x swing): the FY2024 report's own ending cash (2,564,289) vs the
  FY2025 report's restated FY2024 comparative (7,885,711) — a further broadening of the
  CBK-balance component of the definition. Used the restated (FY2025 report) figure. Note
  the FY2023→FY2024 Balance Sheet/Income Statement comparative also has one harmless
  reclassification (Accruals & Provisions ↔ Other Liabilities swapped ~1.07bn between
  reports; Total Liabilities/Assets unaffected) — not a restatement, just a caption move.

## Update 2026-07-06 (yet later) — Shares outstanding, for per-share valuation

Needed a real share count to convert the Valuation sheet's DDM/Residual Income/P-B-ROE
implied equity values into per-share terms. Found directly in the FY2025 report's share
capital note (`Integrated-Report-and-Financial-Statements-2025.pdf`, p.265):

- **Par value: KES 1.00 per ordinary share** (stated explicitly on this page).
- Share capital rollforward: 1,305,195,000 shares at 1 Jan 2025 + 357,459,553 new shares
  issued during 2025 (Restricted Equity Offer by Private Placement, offer price Kshs
  14.50 = Kshs 1.00 par + Kshs 13.50 premium) = **1,662,655,000 shares at 31 Dec 2025**.
  This is the same rollforward pattern as the FY2023 rights issue (643,553,771 new shares
  at the same Kshs 14.50 offer price, 1-for-2 basis) that took shares from 1,287,107,542
  (pre-rights) — both already reflected in `ACTUALS[y]['share_capital']`.
- Because par value is exactly KES 1.00, the share-capital account balance in KES
  millions *is* the share count in millions for every year — `ACTUALS[y]
  ['share_capital']` (already in `config.py`) doubles as that year's share count, no new
  field needed for the historical Book Value Per Share cross-check.
- Note 12 (same PDF, p.244, "Earnings per share – Group & Bank") separately discloses
  the **weighted average** share count used for historical EPS: Bank 1,367,259
  thousand (FY2025) / 1,303,523 thousand (FY2024) — confirms Bank EPS 4.05 (FY2025) and
  2.50 (FY2024) exactly (Bank PAT 5,530,650 / 1,367,259 = 4.0454 ≈ 4.05; 3,261,663 /
  1,303,523 = 2.502 ≈ 2.50). This is a *different*, backward-looking concept from the
  period-end count above — correct for restating a past year's EPS, wrong for valuing
  the *current* share base going forward, which is what the Valuation sheet's per-share
  figures do (hence using the period-end 1,662,655,000 count, not this one).
- Cross-checked the period-end share count against Family Bank's own disclosed Book
  Value Per Share (p.41, already noted above: "Book Value/share 17.15→19.62",
  Consolidated basis): Consolidated Total Equity(FY2025, 32,622.486m) ÷ 1,662.655m =
  **19.62** exactly; (FY2024, 22,389.414m) ÷ 1,305.195m = **17.15** exactly. Confirms the
  share count is right. Our own Bank-basis Total Equity gives a slightly lower BVPS
  (19.31 for FY2025, 16.64 for FY2024) — expected, given this model's Bank-not-Group
  basis (see the Bank vs Consolidated reconciliation above), not a discrepancy.

## Update 2026-07-26 — Equity risk premium, beta, and remaining peer P/B ratios resolved

Closes the three items below that were previously `[PLACEHOLDER]`. All figures pulled via
live web search/fetch (no market-data API); see `examples/family_bank_kenya/config.py`
`VALUATION` dict and `PEER_BANKS` list for where each value now lives.

- **Equity risk premium** — Damodaran's total Kenya ERP (mature-market ERP + country risk
  premium; Moody's Caa1, country risk premium 9.71%) is **13.94%**, from his Jan 2026 data
  update (`pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/ctryprem.html`), replacing
  the earlier 9.5% generic placeholder. **[DISCLOSED]**
- **Beta** — Family Bank itself has no measurable beta yet (NSE listing 23 Jun 2026 is too
  recent for a reliable price history). Used the average of 6 NSE-listed Kenyan peer banks'
  published equity betas instead: Absa 0.44, Co-op Bank 0.52, DTB 0.28, Equity Group 0.59,
  I&M 0.80, KCB Group 0.66 → **average 0.55** (`live.mystocks.co.ke`, accessed 24 Jul 2026).
  Stanbic, StanChart, and NCBA don't publish a beta on this source and were excluded from
  the average rather than estimated. Replaces the earlier 1.0 neutral-midpoint placeholder.
  **[DISCLOSED-DERIVED]**
- **Peer bank P/B ratios** (the 7 remaining after NCBA/I&M) — current NSE share price ÷ book
  value per share, `stockanalysis.com/quote/nase/<ticker>/statistics/`, all accessed 24 Jul
  2026: Absa 1.69 (BVPS 19.58, price 33.00), Co-op Bank 1.18 (BVPS 29.61, price 35.00), DTB
  0.36 (BVPS 377.77, price 150.75, ticker DTK), Equity Group 0.96 (BVPS 86.57, price 87.00),
  KCB Group 0.73 (BVPS 109.61, price 82.50), Stanbic Holdings 1.44 (BVPS 202.74, price
  292.00), StanChart 1.81 (BVPS 184.79, price 334.25, ticker SCBK). **[DISCLOSED-DERIVED]**

Net effect on cost of equity: CoE = risk-free (12.32%) + beta × ERP. Old: 12.32% +
1.0×9.5% = 21.82%. New: 12.32% + 0.55×13.94% ≈ 19.99% — the higher, Kenya-specific ERP and
the lower, measured peer beta largely offset each other, landing CoE about 1.8 points lower
than before.

## Update 2026-07-26 (cont.) — Blended valuation weighting research

Full discussion (Damodaran's stance on triangulation vs. mechanical averaging; how sell-side
analysts actually weight DDM/Residual Income/relative valuation for banks; the sources) lives
in `BLUEPRINT.md`'s "2026-07-26 — Blended valuation, per-scenario valuation, and Net Income
sensitivity" section rather than duplicated here, since it's a methodology/design decision
rather than a company-specific data point. Short version: no universal weighting formula
exists in the literature, so weights (50% DDM / 30% RI / 20% P/B-ROE) operationalize this
model's own pre-existing "primary / cross-check / market-check" method hierarchy, and are
configurable in `config.py`. Key papers: Gianfrate & Vincenzi (*"How Do Analysts Value
Banks?"*), Brownen-Trinh et al. 2023 (*"How Do Equity Research Analysts Value Banks?"*),
Frensidy et al. 2020 (target-price accuracy study), Damodaran's relative-valuation lecture
notes (pages.stern.nyu.edu).

## Still outstanding (see `BACKLOG.md`)

- CBK Prudential Guidelines PDF direct pull (exact current wording, not just figures
  triangulated from Family Bank's own disclosure — those already match secondary sources
  closely, so this is now a lower-priority confirmation, not a blocker).
- Kenyan government bond yield for CAPM risk-free rate: **12.32% (10-year, 2 July 2026,
  Trading Economics)** — secondary source, reasonable to use as-is.
- Re-extraction once the four broken PDFs are replaced: full 2024/2025 IFRS 9 stage
  tables, capital adequacy 5-year trend, segment/sector loan concentration detail.
