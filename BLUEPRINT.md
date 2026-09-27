# Blueprint: Unilever Hyperinflation-Accounting Model

**Status:** Pivoted 2026-09-27 from the generic REIT valuation model (Acorn I-REIT) to a
CFA Level II Financial Statement Analysis teaching model — the *Multinational Operations*
reading, specifically hyperinflation accounting (IAS 29) and its interaction with IAS 21
translation — illustrated with Unilever plc's real disclosed treatment of its Argentina
and Türkiye subsidiaries. The prior REIT-model design history lives in git history and in
`CHANGELOG.md`'s earlier entries — this file starts fresh for the new domain rather than
merging the two; they share no calculation logic (only `bizplan/financial/xl_helpers.py`'s
formula/styling primitives and the `bizplan/config_loader.py` load/validate *pattern*
carry over — the REQUIRED_FIELDS shape itself is entirely rewritten).

## Why this is a different domain, not a REIT re-skin

A REIT's economics center on income-generating property, rental income, and a regulatory
distribution requirement. None of that applies here. This model isn't valuing a company
at all — it's teaching a specific accounting mechanic (how a subsidiary's local-currency
financial statements get restated for inflation, then translated to the parent's
reporting currency, and how that differs under IFRS vs. US GAAP) using a real company's
real disclosed numbers as the calibration target. This is a full rewrite of the
calculation and rendering layers, reusing only:

- `bizplan/config_loader.py` — the load/validate pattern (`REQUIRED_FIELDS`,
  `validate_config`, `load_and_validate`), with an entirely new field list.
- `bizplan/financial/xl_helpers.py` — formula-capable openpyxl primitives (colors,
  `header_row`/`data_row`/`total_row`, `_cell`/formula-string helpers), and the FMI
  data-provenance color convention (blue = disclosed input, dark = internal formula, teal
  = cross-sheet reference, orange = modeled/benchmark proxy).
- The `bizplan/report/*` 7-stage `claude -p` pipeline *shape* (sourcing → ground truth/
  validation → price/consensus research → mechanical pre-decision → drafting → review/
  coherence → PDF), repurposed toward a different question (see "Report pipeline" below)
  rather than discarded.

## The real-world case

Unilever plc reports under IFRS and applies **IAS 29** to its Argentina (hyperinflationary
since 1 Jul 2018) and Türkiye (since 1 Jul 2022) operations: it restates historical-cost
non-monetary assets/liabilities and the income statement for inflation during the period,
then translates the restated figures using **IAS 21's closing rate** (not an average
rate — the correct treatment for a hyperinflationary economy's financial statements,
which are already expressed in a single period-end purchasing-power unit). It discloses
the aggregate impact of that treatment on consolidated Total assets, Turnover, Operating
profit, and Net monetary gain/(loss) each year:

| IAS 29 impact, €m | 2024 Argentina | 2024 Türkiye | 2025 Argentina | 2025 Türkiye |
|---|---:|---:|---:|---:|
| Total assets | +474 | +65 | −199 | −20 |
| Turnover | +230 | +187 | −90 | −16 |
| Operating profit | +10 | −4 | −54 | −46 |
| Net monetary gain/(loss) | −206 | +11 | −46 | −10 |

Sources: Unilever plc Form 20-F, FY2024 and FY2025 (SEC EDGAR) — see
`examples/unilever/config.py`'s `SOURCES` for URLs.

## What this model builds — and its explicit limits

Unilever doesn't disclose subsidiary-level financial statements at the granularity needed
to reconstruct the restatement mechanically. So this model builds a small, fully
hand-traceable **fictional** subsidiary for Argentina and for Türkiye, algebraically
solved (not guessed) so that running it through the model's engine reproduces the real
**2024** disclosed impact figures almost exactly, then rolls the same model forward into
**2025** (not re-solved) as an out-of-sample validation against the real 2025 figures —
with the resulting gap documented, not hidden. Full derivation, citations, and the "what
this model is and isn't" caveat live in `examples/unilever/research_output.md` — read it
before treating any subsidiary-level figure in this model as a real Unilever disclosure.
It isn't; only the four aggregate impact numbers per subsidiary per year are real.

## Config schema (`bizplan/config_loader.py`, `examples/<institution>/config.py`)

`REQUIRED_FIELDS`: `BUSINESS_NAME`, `OUTPUT_PREFIX`, `CURRENCY`, `YEARS`, `ACTUAL_YEARS`,
`SUBSIDIARIES` (per-subsidiary local currency, hyperinflationary-since date, item
classification), `INFLATION_INDICES` (opening/closing general price index per subsidiary
per year), `FX_RATES` (opening/closing local-per-EUR per subsidiary per year),
`ACCOUNTING_SCENARIOS` (the three World definitions), `ACTUALS` (per-subsidiary
local-currency nominal inputs per year), `VALIDATION_ACTUALS` (real disclosed roll-forward
year's impact figures), `CONSENSUS`, `VALUATION`. Also `DISCLOSED_IMPACT_2024` (the primary
calibration target), `OTHER_GROUP_OPERATIONS_EUR`, `SOURCES` — read defensively, not in
`REQUIRED_FIELDS`, but needed by the calculation engine and renderer respectively.

## Calculation engine (`bizplan/financial/hyperinflation_calculations.py`)

For each subsidiary and year, `restate_and_translate()` computes three parallel "worlds"
from the same local-currency nominal inputs:

- **World A — plain current-rate method**: no inflation restatement; balance sheet at the
  closing FX rate, income statement at the average FX rate. The "disappearing plant"
  baseline the real IAS 29 impact is measured against.
- **World B — US GAAP temporal method**: monetary items at the current (closing) rate,
  non-monetary items at historical rates, most P&L at the average rate — producing an FX
  *remeasurement* gain/loss, a genuinely different mechanism from IAS 29's purchasing-power
  monetary gain/loss, not just a different number for the same thing.
- **World C — actual IFRS treatment**: IAS 29 restatement (monetary items unchanged,
  non-monetary items restated by the price-index change since acquisition, income
  statement items restated from an in-year average), then IAS 21 translation of the
  restated figures at the closing rate. This is what Unilever actually reports.

Both the IAS 29 net monetary gain/(loss) and World B's remeasurement gain/(loss) are
computed as a **balancing plug** (restated/remeasured Assets − Liabilities − Equity − Net
income) — this is how IAS 29 actually works, and it guarantees the restated balance sheet
ties out by construction rather than by an approximate formula. `build_model(config)` is
the single entry point: runs every subsidiary through all three worlds for every year,
consolidates with the rest of the group (`consolidate()`), and validates the primary
year's impact against `DISCLOSED_IMPACT_2024` / later years against `VALIDATION_ACTUALS`
(`validate_against_disclosed()`).

**A finding worth flagging** (see `research_output.md` for the full discussion): the
common CFA heuristic "net monetary liability → gain, net monetary asset → loss" holds
exactly only in a static, single-item setting. In this full model, Argentina's solved net
monetary position is a *liability*, yet it still shows a net monetary *loss* — because the
plug also nets against the growth of the other restated items (equity, operating profit).
The simple heuristic is a starting intuition, not a formula that survives a full
consolidated restatement.

## Excel renderer (`bizplan/financial/hyperinflation_excel_renderer.py`)

Every calculated cell is a live Excel formula (verified with the `formulas` Python
package — a real formula evaluator, not just openpyxl string-writing — reproducing the
Python engine's output to full precision). Sheets: Cover, Assumptions (raw local-currency
inputs only — BLUE), one schedule sheet per subsidiary (`Argentina_Schedules`,
`Turkiye_Schedules` — each walking 01 Local FS → 02 Inflation Index → 03 IAS 29
Restatement → 04 FX Translation (World C) → World A → World B → IAS 29 Impact, so the
whole restatement mechanic is traceable on one sheet, with cross-sheet TEAL references
back to Assumptions and DARK internal formulas for everything derived), Consolidation
(World C group totals + ratios), Scenario_Comparison (World A/B/C **side by side** — the
user's own requested table shape, for both years), Validation_2025, Sources.

**Deliberate deviation from the REIT model's `CHOOSE()` scenario-switch convention**:
World A/B/C are shown permanently side by side, not switched via one scenario cell —
comparing all three simultaneously is the actual pedagogical point here, not picking one.

## Report pipeline (`bizplan/report/*`, `.devops/agents/equity-report/`)

Same 7-stage shape as the REIT pipeline, repurposed toward a different question: how does
each subsidiary's hyperinflation treatment affect Unilever's consolidated numbers, and
does the market/analyst consensus price that correctly — or does it fold a real,
quantified effect into generic "FX headwind" noise? Stage 3's mechanical pre-decision is a
materiality flag (net monetary gain/loss as a % of group operating profit), not a
NAV/DDM/cap-rate price-vs-fair-value call — this model doesn't build a full equity
valuation. The Recommendation section (Stage 4) combines that flag with Stage 2's real
consensus research to argue an actual Buy/Hold/Sell-style call specifically about
earnings-quality mispricing. See `AGENTS.md` for the full stage-by-stage breakdown and
current verification status.

## Known simplifications (see `research_output.md` for full detail and citations)

- **Single aggregate non-monetary bucket** per subsidiary (inventory + PPE combined),
  rather than item-level restatement with separate acquisition-date vintages.
- **Geometric-mean average index/FX** stands in for a full monthly series.
- **Opening equity and the monetary-asset/liability split are free modeling choices** —
  solved algebraically to hit the four real disclosed 2024 targets, but not themselves
  derived from any Unilever disclosure.
- **Total-assets impact structurally cannot flip sign** in this model (pure inflation
  restatement can only raise non-monetary asset values) — the real 2025 disclosure shows
  a negative one, which this model's 2025 roll-forward doesn't reproduce; documented as an
  open limitation, not resolved.
- **`OTHER_GROUP_OPERATIONS_EUR`** is an illustrative scale, not Unilever's real
  consolidated ex-Argentina/Türkiye figures.

## Follow-up work (not in this pass — see `BACKLOG.md`)

**BBVA/Garanti** (the "advanced" case identified alongside Unilever — a Spanish bank
applying IAS 29 to both its Türkiye (Garanti BBVA) and Argentina (BBVA Argentina)
subsidiaries, with Garanti separately publishing its own full IFRS statements, enabling an
actual subsidiary-to-parent reconstruction rather than a calibrated fictional one) is
deliberately deferred, not built in this pass.
