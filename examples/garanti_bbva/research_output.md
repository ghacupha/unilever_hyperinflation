# Garanti BBVA — net monetary position reconstruction (research notes)

Companion to `config.py` / `Garanti_BBVA_Monetary_Position.xlsx`. Where
`examples/unilever/research_output.md` documents a **calibrated fictional** subsidiary
solved to reproduce Unilever's real disclosed aggregate impact, this document covers an
**attempted real reconstruction**: every input number is Garanti BBVA's own published
figure, and the model's output is an independent estimate checked against Garanti's own
disclosed result — not solved to match it.

## What this is and isn't

- **Is**: Türkiye Garanti Bankası AŞ (Garanti BBVA)'s real, as-published Consolidated
  Statement of Financial Position and Statement of Profit or Loss, IFRS basis, IAS
  29-restated, for FY2024 and FY2025, copied line-by-line from its own IFRS Financial
  Reports PDF (`IFRS-Financials-31122025.pdf`, 3 pages: a table of contents and the two
  primary statements — no notes). Garanti discloses "Gain/(loss) on net monetary
  position, net" as an explicit P&L line: **−TL 5,327,505 thousand** (FY2025) and
  **−TL 12,278,662 thousand** (FY2024) — a real figure, not something this model has to
  derive to get *any* answer.
- **Isn't**: a note-level, item-by-acquisition-vintage restatement audit. Garanti's
  publicly posted "IFRS Financials" document is a 2-statement summary, not a full
  audited annual report with notes — it doesn't disclose the general price index it used,
  which specific items were restated from which acquisition dates, or any inflation-
  linked-bond / hedge breakdown within "Investment securities." Those would be needed for
  a genuine ground-up restatement; what's built here instead is the next-best real
  exercise — classify the real disclosed balance sheet into monetary/non-monetary,
  independently *estimate* the monetary result from that classification plus a public CPI
  series, and see how close that estimate lands to Garanti's own real disclosed number.

## Why the 2024 column needs "un-restating"

IAS 29 ¶34 requires comparative amounts in a hyperinflationary entity's financial
statements to be restated into the *current* period's measuring unit — so Garanti's
FY2025 report presents **both** the FY2025 and FY2024 columns in **December-2025**
purchasing-power terms. That's correct IFRS presentation, but it means the FY2024 column
as shown is *not* the balance Garanti itself would have reported a year earlier (in its
own FY2024 report, expressed in December-2024 terms) — it's that balance multiplied by
the Dec-2024→Dec-2025 CPI ratio.

To estimate FY2025's monetary result from the *opening* (1 Jan 2025) net monetary
position, that opening position needs to be in its own (Dec-2024) purchasing-power
terms — otherwise the inflation factor would effectively be applied twice. `bank_
monetary_position.recover_original_purchasing_power()` divides the as-shown comparative
back out by the CPI ratio to recover it:

```
NMP(Dec-2024, as shown in the FY2025 report, Dec-2025 terms) = TL 326,971,330 thousand
CPI(Dec-2024) / CPI(Dec-2025) = 1,029.82 / 1,348.17 = 0.76388
NMP(Dec-2024, its own Dec-2024 terms)                         = TL 249,751,985 thousand
```

## The estimate

Standard single-period approximation (same simplification category as the Unilever
model's geometric-mean-average-index stand-in for a full monthly series): monetary
gain/(loss) for the year ≈ opening net monetary position (in its own period's purchasing
power) × the period's CPI growth rate, sign-flipped — a net monetary *asset* position
loses real value as prices rise, a net monetary *liability* position gains.

```
FY2025 CPI growth = 1,348.17 / 1,029.82 − 1 = 30.9%
Estimated monetary gain/(loss) = −TL 249,751,985 thousand × 30.9% ≈ −TL 77.2 billion
Garanti's own disclosed figure                                    =  −TL 5.3 billion
Gap                                                                ≈ 14.5×
```

Both years' loan/deposit books put Garanti in a **net monetary asset position** (unlike
Unilever's Argentina, which the existing model finds to be a net monetary *liability*
that still books a loss) — so the sign of the estimate (a loss) is directionally right.
The *size* is off by an order of magnitude.

## Why the gap is large — a real finding, not a bug

This repo's convention (see `BLUEPRINT.md`'s "Known simplifications" for the Unilever
model) is to document a gap like this rather than tune inputs until it disappears — tuning
would turn a real reconstruction back into a calibrated one, defeating the point of using
Garanti's actual disclosures. Three honest reasons this estimate overstates Garanti's
real monetary loss by ~14x:

1. **A bank's monetary position isn't static for a year.** The opening-balance
   approximation assumes the Dec-2024 net monetary asset position was held constant
   through the year before "losing value" to inflation. A bank's loan book and deposit
   base turn over continuously — new loans originate, deposits flow in and out, debt is
   issued and repaid — so the *average* exposure during the year can differ substantially
   from either endpoint snapshot. (Using the average of the two endpoints instead of the
   opening balance makes the estimate *worse*, not better, here — Garanti's net asset
   position grew over the year, so an average-based estimate would overstate the loss by
   even more. The opening-only approximation is already the more favorable of the two
   naive choices.)
2. **A real bank actively manages its inflation exposure.** Turkish banks are known to
   hold CPI-linked ("TLREF"/inflation-indexed) government securities specifically to
   hedge monetary-position risk — their fair value rises with inflation, offsetting the
   loss elsewhere. This model classifies "Investment securities" (TL ~530bn, ~12% of
   total assets) as a plain monetary item because the 3-page summary statement doesn't
   break out how much of that balance is inflation-linked versus plain fixed-rate TL debt
   — if a large share is CPI-linked, its inflation protection would already be captured
   through fair-value gains elsewhere in the P&L (trading income, interest income),
   not visible as part of the "net monetary position" this model computes. This is
   exactly the "protective asset" nuance BBVA Group's own disclosures reference for its
   hyperinflationary subsidiaries, and it isn't recoverable from the summary statement
   alone.
3. **Unlike Unilever, a bank's whole business model is about managing monetary-item
   risk**, not incidentally bearing it as a side effect of selling physical goods. The
   large, real gap here is itself the pedagogical point: the "static opening position ×
   inflation" approximation that works reasonably well for a non-financial company's
   balance sheet (where monetary items are a side effect of ordinary working-capital
   accounts) breaks down for an institution whose core activity *is* actively trading
   and hedging monetary exposure.

## Classification used (see `config.py`'s `BALANCE_SHEET`)

**Non-monetary** (restated/not treated as monetary): Equity investments, Assets held for
sale, Investment properties, Tangible and intangible assets, Deferred tax asset/liability
— the standard IAS 29 non-monetary set for a bank, a much shorter list than a
manufacturer's (no inventory, no PP&E-heavy operating base).

**Monetary** (everything else): Cash and central-bank balances, FVTPL financial assets,
derivatives, loans and advances (to banks and customers), investment securities, other
assets; all deposit/funding liabilities, FVTPL financial liabilities, derivatives,
subordinated liabilities, current tax liability, provisions, other liabilities. This is
the simplification flagged in point 2 above — in particular, "Investment securities" and
"Other assets" are classified monetary wholesale, without a further split.

## Scope explicitly deferred (BACKLOG.md Phase 5b)

- **BBVA Argentina**: its own separately filed statements follow Argentina's BCRA
  "Group C" prudential basis, not pure IFRS, and explicitly disable IFRS 9 §5.5
  impairment — a different accounting basis layered on top of the same hyperinflation
  question, which would need its own careful basis-reconciliation discussion before any
  numbers could be compared to Garanti's or Unilever's. Not attempted this pass.
- **A full report-pipeline run** (`bizplan/report/*`, the `claude -p`-driven stages) for
  this instance — this pass is scoped to the core reconstruction (calculation engine +
  Excel model + tests), not the narrative equity-research-report layer.
- **Note-level restatement detail** (the general price index Garanti itself used, item
  vintages, the inflation-linked-securities breakdown) — would require a fuller annual
  report with notes, which wasn't located as a public PDF this session; the dedicated
  "IFRS Financial Reports" page only hosts the 2-statement summary used here.

## Sources

- Türkiye Garanti Bankası AŞ and Its Subsidiaries, Consolidated Financial Statements
  (IFRS basis), As of and For the Year Ended 31 December 2025 — Garanti BBVA Investor
  Relations, IFRS Financial Reports (`IFRS-Financials-31122025.pdf`).
- TÜİK (Turkish Statistical Institute) Consumer Price Index, 2003=100 base, December
  2023/2024/2025 index values — sourced via aggregated secondary reporting and
  cross-checked against the widely reported +44.38% (2024) and +30.89% y/y (December
  2025) CPI inflation rates for Türkiye; TÜİK's own site wasn't directly fetchable this
  session.
