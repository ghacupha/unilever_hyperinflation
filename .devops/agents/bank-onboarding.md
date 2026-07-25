# Bank / financial-institution onboarding SOP

Institution-agnostic playbook for bringing a new bank into this repo's
financial model generator. This is the authoritative process the `agent/`
CLI's system prompt is grounded in — it's a direct distillation of
`BACKLOG.md`'s proven Phase -0.5 through Phase 11, the record of what
actually worked (and what broke) onboarding Family Bank Kenya.

## 1. Data intake

Locate the institution's public filings (annual reports, quarterly
statements, IPO/listing prospectus, MTN/bond information memoranda — any of
these can carry the granular disclosure the schema below needs). Before
extracting anything, **validate each downloaded PDF opens and has a sane
page count** — this is a recurring real risk, not a one-off: 4 of 8 source
PDFs were found broken (truncated on disk, or missing their `/Pages`
catalog) during Family Bank Kenya's onboarding. A PDF that fails to open
cleanly needs re-fetching before it's trusted as a source.

## 2. Targeted extraction, not cover-to-cover reads

Don't read filings end to end. Extract text/tables once, then search for the
handful of terms that matter: "Stage 1"/"Stage 2"/"Stage 3", "expected
credit loss", "non-performing", "capital adequacy", "liquidity ratio",
"segment information", "core capital". Jump straight to those pages. File
size should not translate into token spend.

Pull, specifically:
- Full balance sheet, income statement, cash flow statement (at least the
  most recent 1-3 years, both **Bank/standalone and Consolidated/Group**
  columns if both are disclosed — model on the Bank-only column; see the
  "Bank vs Consolidated" pitfall below).
- IFRS 9 stage table by product/segment (not customer segment, unless
  that's genuinely how the institution discloses it).
- Capital adequacy note (Tier 1/Tier 2 build-up, RWA, regulatory minimums).
- Off-balance-sheet exposure, disclosed **separately** from on-balance-sheet
  loans — keep it that way in the config; never fold it into the loan
  tables, since disclosure conventions vary by institution.
- Peer comparables if disclosed (EPS/ROAE/payout/DPS, P/B where derivable
  from book value + share price).
- Sector/macro outlook relevant to the institution's home market.

## 3. Known pitfalls (from the Family Bank Kenya build)

- **Bank vs Consolidated (Group) confusion.** Annual reports usually
  disclose both columns side by side. A bank that sits inside a group
  should be modeled on its own **Bank/standalone** column — using the
  Consolidated column by mistake is an easy, hard-to-notice error since
  both columns look plausible in isolation.
- **Cash-flow-statement cash vs. balance-sheet cash are not the same
  number.** The CF statement's "cash and cash equivalents" and the balance
  sheet's "cash and balances with the central bank + due from banks" differ
  by inter-bank balances. Use each figure only where it belongs — conflating
  them breaks the Balance Sheet Check by exactly the inter-bank-balances
  amount.
- **Regulatory Tier 1 ≠ total accounting equity.** Don't assume the balance
  sheet's equity figure is the regulatory capital base — find the
  institution's own Capital Management note for the real Tier 1/Tier 2
  build-up (share capital/premium/retained earnings minus deferred tax
  assets for Tier 1; revaluation/subordinated debt/statutory reserve for
  Tier 2).

## 4. Write `research_output.md`

Per-institution, in `examples/<institution>/research_output.md`, with a
`source`/`accessed` field per datapoint — this is the audit trail every
`config.py` value traces back to. Mirror
`examples/family_bank_kenya/research_output.md`'s structure.

## 5. Populate `config.py`

Against the hard schema contract in `bizplan/config_loader.py`:
`REQUIRED_FIELDS` (`BUSINESS_NAME, OUTPUT_PREFIX, CURRENCY, YEARS, TAX_RATE,
LOAN_SEGMENTS, DEPOSIT_TYPES, INVESTMENT_SECURITIES, OPEX_ITEMS, CAPITAL,
MACRO_SCENARIOS, VALUATION, PEER_BANKS, ACTUALS, ACTUAL_YEARS,
REGULATORY_CAPITAL`) plus the shape-level checks in `validate_bank_config()`
(each `LOAN_SEGMENTS` entry needs specific keys; `MACRO_SCENARIOS` weights
must sum to 1.0). Use `examples/family_bank_kenya/config.py` as the
structural template — same section-header comments, same field names.

## 6. Run the existing renderer, unchanged

```
python scripts/build_bank_model.py --bank <institution>
```

or `--config <path>` for an explicit path. Never modify
`bizplan/financial/bank_calculations.py` or
`bizplan/financial/bank_excel_renderer.py` for a new institution — those
stay institution-agnostic by design; only `examples/<institution>/` and
`data/<institution>/` are the new institution's own.

## 7. Verify

- The Model sheet's built-in Master Check (Balance Sheet / Capital Adequacy
  / Liquidity) is a live formula — inspect it, but note the final "OK"
  confirmation needs a real Excel open to recalculate (no LibreOffice
  available in this environment to do it headlessly).
- Spot-check a few modeled figures against the real disclosed actuals
  (net loans, deposits, NII, capital ratio) — a few percent off is normal
  for a first pass; anything wildly off usually means a Bank-vs-Consolidated
  or cash-definition mixup (see §3).

## 8. Seasonal updates

When a new annual or quarterly filing is published: find it, extract the
new period's actuals, then mechanically roll the config forward — move the
value that was the nearest **projected** year into `ACTUALS`/`ACTUAL_YEARS`
now that a real figure exists for it, and extend `YEARS` by one more forward
year to hold the projection horizon constant. This is exactly the
established pattern already used once in this repo (the opening basis
moved from FY2023 to FY2025 actuals as real data became available). Preserve
every other field — a seasonal update is a roll-forward, not a rewrite.
