# Model sourcing SOP (hyperinflation-accounting domain)

Given an institution (currently only `unilever`), verifies/refreshes
`examples/<institution>/config.py` + `research_output.md` against the institution's real
disclosed IAS 29 hyperinflation-accounting figures.

Unlike the prior REIT/bank pipeline, this is **not** a rolling multi-year forecast with an
as-of anchor year to re-source each quarter. It's a fixed calibration exercise: a small,
fully hand-traceable fictional subsidiary per hyperinflationary operation, sized so the
model's IAS 29 restatement + IAS 21 translation reproduces the institution's **real
disclosed primary year** (2024 for Unilever) impact figures almost exactly, then a
**validation year** (2025) the model is rolled forward into and compared against — not
re-solved to fit. See `examples/unilever/research_output.md`'s "Calibration method" and
"2025 roll-forward validation" sections for the full worked derivation.

## 1. What this stage actually does

- **Already-onboarded institution** (the normal case — `examples/<institution>/config.py`
  already exists): read it and `research_output.md`'s "Calibration method" section, then
  verify the config's local-currency subsidiary inputs still reproduce
  `config.DISCLOSED_IMPACT_2024` when run through
  `hyperinflation_calculations.build_model()`. Only change a figure if the institution has
  since **restated or re-disclosed** it (e.g. a later annual report revises a prior-year
  IAS 29 impact table) — this is a verification/refresh pass, not a re-derivation from
  scratch. Do not touch `SUBSIDIARIES`, `INFLATION_INDICES`, or `FX_RATES` unless the
  underlying disclosed macro figures (CPI, FX) have themselves been revised.
- **New institution**: full onboarding — research the institution's real disclosed IAS 29
  impact table for its hyperinflationary subsidiaries, its subsidiaries'
  hyperinflationary-since dates, and its own disclosed general-price-index/FX assumptions
  where available, then solve backward for local-currency subsidiary inputs the same way
  `examples/unilever/research_output.md`'s "Calibration method" does (turnover/operating-
  profit impact fixes revenue/cost levels via the inflation-vs-FX wedge; total-assets
  impact fixes the non-monetary asset base; net monetary gain/loss is solved as the
  balancing plug). Document every free modeling choice (opening equity, the monetary
  asset/liability split) explicitly — they are not derived from any disclosure.

## 2. Data intake

The institution's own annual report / Form 20-F (or local-jurisdiction equivalent)
hyperinflation accounting policy note is the primary source — search for "IAS 29",
"hyperinflation", or the specific subsidiary/country name. Cross-check against the
regulator's own filing archive (e.g. SEC EDGAR for a US-listed or SEC-filing foreign
private issuer) for the exact figures rather than a secondary press summary. Extract the
targeted note/table rather than reading the full filing cover-to-cover.

## 3. Known pitfalls (hyperinflation-accounting domain)

- **The disclosed "impact" table's comparative baseline may not be fully specified.**
  Unilever's headline table gives four aggregate deltas (Total assets/Turnover/Operating
  profit/Net monetary gain-or-loss) but not the full note text explaining every
  contributing effect — e.g. this model's 2025 validation pass found the total-assets
  impact can never flip negative under pure inflation-restatement mechanics alone (see
  research_output.md), yet Unilever's real 2025 disclosure shows a negative one, implying
  some other effect (disposals, impairments, a different comparative convention) not
  visible from the summary table. **Document what you can't reconcile — do not force a
  match by fabricating an assumption that isn't disclosed anywhere.**
- **Two currencies, two different mechanisms can look similar but aren't.** A net
  monetary *loss* doesn't simply mean "net monetary liability position" once the whole
  balance sheet (including restated equity/profit growth) is solved together — see
  research_output.md's "A finding worth flagging" section. Don't assume the simple CFA
  heuristic (net monetary asset → loss, net monetary liability → gain) holds in a full
  consolidated model without checking.
- Same sourcing/citation discipline as any other model in this repo: never fabricate a
  figure; where something genuinely isn't disclosed, use a clearly-marked `[PLACEHOLDER]`
  and note it in `research_output.md`.

## 4. Populate `config.py`

Schema contract is `bizplan/config_loader.py`'s `REQUIRED_FIELDS` + `validate_config()`
shape checks — see `BLUEPRINT.md`'s "Config schema" section for the full field list
(`SUBSIDIARIES`, `INFLATION_INDICES`, `FX_RATES`, `ACCOUNTING_SCENARIOS`, `ACTUALS`,
`DISCLOSED_IMPACT_2024`, `VALIDATION_ACTUALS`, `CONSENSUS`, `VALUATION`, `SOURCES`).

## 5. Run the renderer, unchanged

```
python scripts/build_unilever_model.py --instance <institution>
```

## 6. Validate — a real pass/fail, not just "inspect the formula"

```python
from bizplan.config_loader import load_and_validate
from bizplan.report import data as report_data, validation as report_validation

config = load_and_validate("examples/<institution>/config.py")
computed = report_data.compute(config)
validation = report_validation.validate_model(config, computed)
assert validation["ok"], validation
```

If `validation["ok"]` is `False`, the model's 2024 calibration no longer reproduces the
real disclosed 2024 impact figures within tolerance (±0.5 EURm per line) — fix `config.py`
before proceeding to any later pipeline stage. The 2025 validation year is diagnostic, not
gating (see `bizplan/report/validation.py`'s module docstring for why).

## 7. Write `research_output.md`

Source + accessed date per datapoint, provenance-tagged (`[DISCLOSED]`,
`[DISCLOSED-DERIVED]`, `[MODELED]`, `[PLACEHOLDER]` — see
`examples/unilever/research_output.md` for the convention). Explicitly document any
reconciliation gaps found in the source filings (§3 above) rather than silently resolving
them one way and moving on.
