# Model sourcing SOP (period-parameterized, REIT domain)

Given a REIT/REOC instance (name/ticker, new or already onboarded) and an **as-of anchor
year**, produces `examples/<instance>/config.py` + `research_output.md` whose
actuals/projection windows are derived mechanically from that anchor, not from
"whatever's most recent":

```
ACTUAL_YEARS     = [as_of - 2, as_of - 1, as_of]        # 3 actual years, ending at the anchor
YEARS (projected) = [as_of + 1, ..., as_of + 5]          # 5 years forward from the anchor
```

This is what makes the same instance re-runnable at a different historical vantage point
(e.g. `as_of=2023` instead of `as_of=2025`) — including **backward** re-sourcing for
backtesting, where the point is to research the REIT exactly as it stood at that past
date, not with the benefit of hindsight. If `as_of` is in the past relative to today,
**do not use any filing, price, or news dated after `as_of`'s fiscal year-end filing date**
— that's the entire point of a backtest; leaking later information invalidates it.

## 1. Determine the actuals/projection window

Given `instance` and `as_of`, compute the two year-lists above before doing anything else.
Then:

- **New instance** (no existing `examples/<instance>/config.py`): full onboarding per §2-§4
  below, scoped specifically to filings covering `ACTUAL_YEARS` — not simply "the latest
  available annual report." If the REIT's most recent filing is for a later year than
  `as_of`, that's fine for context but its figures must not leak into `ACTUALS` or influence
  assumption calibration (see backtest note above).
- **Already-onboarded instance, `as_of` later than its current anchor** (rolling forward):
  move the nearest projected year(s) into `ACTUALS` as real figures become available,
  extend `YEARS` to keep the 5-year horizon. Preserve every other field; a roll-forward is
  not a rewrite.
- **Already-onboarded instance, `as_of` earlier than its current anchor** (rolling
  backward, for backtesting): re-derive `ACTUALS`/`YEARS` for the earlier window from the
  filings that existed as of that date. `VALUATION` inputs (risk-free rate, ERP, beta, cap
  rate, peer NAV discount/premium) must also be re-sourced as of `as_of`, not carried
  forward from today's values — a backtest that quietly uses today's cost-of-equity/cap-rate
  inputs to value a three-year-old snapshot isn't testing anything real.

## 2. Data intake

A REIT's own investor-relations site (REIT Manager's site, e.g. Acorn's
`acornholdingsafrica.com`) is usually the best primary source — look for annual reports and
semi-annual/interim reports, which contain the full primary financial statements (statement
of profit or loss, statement of financial position, statement of changes in trust's equity,
statement of cash flows) plus notes. Cross-check against the Nairobi Securities Exchange
(NSE)/Capital Markets Authority (CMA) disclosure archives and any sector-wide equity
analysis reports for headline full-year figures when only interim detail is directly
available. Extract targeted text/tables and search for key terms rather than reading a
200+ page filing cover-to-cover.

## 3. Known pitfalls (REIT-specific)

- **Units-in-issue vs. reported NAV/unit reconciliation gap**: cross-multiplying a
  disclosed units-in-issue roll-forward against disclosed NAV frequently does not exactly
  reproduce the REIT's own reported "NAV per unit" headline (a small, consistent 1-2% gap
  is common) — most likely a weighted-average-vs-point-in-time unit-count convention
  difference on the REIT's side, not a data error. Use the most explicitly-labeled,
  purpose-built roll-forward table for the `UNITS`/`ACTUALS[year]["units_in_issue"]`
  schedule, and document the gap in `research_output.md` rather than silently forcing a
  match — see `examples/acorn_i_reit/research_output.md` for a worked example.
- **Internally inconsistent note tables**: a filing's own notes can disagree with its
  primary statements (e.g. a "movement in units issued" mini-table showing a different
  issuance figure than the Statement of Changes in Equity's own roll-forward for the same
  period) — when this happens, the primary statements (P&L, Balance Sheet, Statement of
  Changes in Equity, Cash Flow) are the more authoritative source; treat note-level
  sub-tables as secondary.
- **Full-year headline vs. interim detail**: sector-wide equity analysis reports often give
  only full-year headline figures (net profit, NAV/unit, dividend) without the granular
  income-statement/balance-sheet detail a live-formula model needs. Where only an interim
  (e.g. H1) report gives full detail, back-solve the remainder (e.g. H2 = FY total − H1
  actual) and tag it `[DISCLOSED-DERIVED]`, not `[DISCLOSED]`.
- **Distributable Income ≠ Net Profit**: a REIT's regulatory distribution requirement is
  computed on Distributable Income (Net Profit minus non-cash items — fair value gains/
  losses on investment property, bargain-purchase gains, impairment reversals), not on Net
  Profit itself. Don't apply the payout-ratio check to the wrong base figure.
- **I-REIT vs. D-REIT regulatory limits differ**: the CMA's REIT regulations set different
  gearing/asset limits for Income REITs vs. Development REITs (an I-REIT holds completed
  income-generating property; a D-REIT develops it) — confirm which type the instance is
  before populating `REGULATORY` (the 35%/40% gearing limit and 80% distribution minimum
  in `examples/acorn_i_reit/config.py` are I-REIT-specific; re-verify against the CMA REITs
  Regulations 2013 FAQ for a D-REIT or a REIT in a different jurisdiction).
- Same sourcing/citation discipline as any other model in this repo: never fabricate a
  figure; where something genuinely isn't disclosed, use a clearly-marked `[PLACEHOLDER]`
  and note it in `research_output.md`.

## 4. Populate `config.py`

Schema contract is `bizplan/config_loader.py`'s `REQUIRED_FIELDS` + `validate_reit_config()`
shape checks — see `BLUEPRINT.md`'s "Config schema" section for the full field list
(`PROPERTIES`, `RENTAL_INCOME`, `OPEX_ITEMS`, `CAPITAL`, `UNITS`, `REGULATORY`,
`MACRO_SCENARIOS`, `SCENARIO_MULTIPLIERS`, `VALUATION`, `PEER_REITS`, `ACTUALS`, ...). Also
add `TICKER`/`EXCHANGE` (e.g. `TICKER = "ACORNI"`, `EXCHANGE = "NSE"`) if the instance is
exchange-listed — optional, not in `REQUIRED_FIELDS`, but Stage 2
(`bizplan/report/price_research.py`) reads them as its default so `--ticker`/`--exchange`
don't need to be passed by hand on every run.

## 5. Run the renderer, unchanged

```
python scripts/build_reit_model.py --reit <instance>
```

## 6. Validate — a real pass/fail, not just "inspect the formula"

```python
from bizplan.config_loader import load_and_validate
from bizplan.report import data as report_data, validation as report_validation

config = load_and_validate("examples/<instance>/config.py")
computed = report_data.compute(config)
validation = report_validation.validate_model(config, computed["results"])
assert validation["ok"], validation
```

If `validation["ok"]` is `False`, do not proceed to any later pipeline stage — fix the
`config.py` inputs until every year's Balance Sheet, LTV, and Income-Producing-% checks
pass, and every *projected* year's Payout check passes (the Payout check is expected to
read `False` for actual years whose real disclosed payout ratio is genuinely below the
CMA's 80% minimum — a governance fact, not a modeling error; see
`bizplan/report/validation.py`'s module docstring). This mirrors the Model sheet's Master
Check exactly (same four checks, same tolerances, same actual-year payout exception).

## 7. Write `research_output.md`

Source + accessed date per datapoint, provenance-tagged (`[DISCLOSED]`,
`[DISCLOSED-DERIVED]`, `[MODELED]`, `[MACRO]`, `[PLACEHOLDER]` — see
`examples/acorn_i_reit/research_output.md` for the convention), plus: record the `as_of`
anchor year explicitly at the top of the file, so a reader immediately knows which vantage
point this particular sourcing run represents — this matters once the same instance has
more than one `research_output.md`-worthy run at different anchors. Explicitly document any
reconciliation gaps found in the source filings (§3 above) rather than silently resolving
them one way and moving on.
