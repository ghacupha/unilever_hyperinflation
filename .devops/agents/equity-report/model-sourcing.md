# Model sourcing SOP (period-parameterized)

Generalizes `.devops/agents/bank-onboarding.md` along a second axis: not just *which*
institution, but *as of which year*. Every invocation of this SOP is given two inputs —
an institution (name/ticker, new or already onboarded) and an **as-of anchor year** — and
must produce a `config.py` whose actuals/projection windows are derived mechanically from
that anchor, not from "whatever's most recent":

```
ACTUAL_YEARS     = [as_of - 2, as_of - 1, as_of]        # 3 actual years, ending at the anchor
YEARS (projected) = [as_of + 1, ..., as_of + 5]          # 5 years forward from the anchor
```

This is what makes the same institution re-runnable at a different historical vantage
point (e.g. `as_of=2023` instead of `as_of=2025`) — including **backward** re-sourcing for
backtesting, where the point is to research the institution exactly as it stood at that
past date, not with the benefit of hindsight. If `as_of` is in the past relative to today,
**do not use any filing, price, or news dated after `as_of`'s fiscal year-end filing date**
— that's the entire point of a backtest; leaking later information invalidates it.

Everything in `bank-onboarding.md` §1-§4 (data intake, targeted extraction, known
pitfalls, `research_output.md` sourcing discipline) applies unchanged and is not repeated
here. This file only adds the period-parameterization layer and generalizes §5-§8.

## 1. Determine the actuals/projection window

Given `institution` and `as_of`, compute the two year-lists above before doing anything
else. Then:

- **New institution** (no existing `examples/<institution>/config.py`): full onboarding
  per `bank-onboarding.md` §1-§2, but scoped specifically to filings covering
  `ACTUAL_YEARS` — not simply "the latest available annual report." If the institution's
  most recent filing is for a later year than `as_of`, that's fine for context but its
  figures must not leak into `ACTUALS` or influence assumption calibration (see backtest
  note above).
- **Already-onboarded institution, `as_of` later than its current anchor** (rolling
  forward): this is `bank-onboarding.md` §8's existing "seasonal update" pattern — move
  the nearest projected year(s) into `ACTUALS` as real figures become available, extend
  `YEARS` to keep the 5-year horizon. Preserve every other field; a roll-forward is not a
  rewrite.
- **Already-onboarded institution, `as_of` earlier than its current anchor** (rolling
  backward, for backtesting): re-derive `ACTUALS`/`YEARS` for the earlier window from the
  filings that existed as of that date. `VALUATION` inputs (risk-free rate, ERP, beta,
  peer P/B) must also be re-sourced as of `as_of`, not carried forward from today's
  values — a backtest that quietly uses today's cost-of-equity inputs to value a
  three-year-old snapshot isn't testing anything real.

## 2. Populate `config.py`

Same schema contract as `bank-onboarding.md` §5 (`bizplan/config_loader.py`'s
`REQUIRED_FIELDS` + `validate_bank_config()` shape checks) — nothing new here except that
`ACTUAL_YEARS`/`ACTUALS` and `YEARS` are now derived from `as_of` per §1 above, not chosen
freehand. Also add `TICKER`/`EXCHANGE` (e.g. `TICKER = "FMLY"`, `EXCHANGE = "NSE"`) if
the institution is exchange-listed — optional, not in `REQUIRED_FIELDS`, but Stage 2
(`bizplan/report/price_research.py`) reads them as its default so
`--ticker`/`--exchange` don't need to be passed by hand on every run.

## 3. Run the renderer, unchanged

Same as `bank-onboarding.md` §6:

```
python scripts/build_bank_model.py --bank <institution>
```

## 4. Validate — now a real pass/fail, not just "inspect the formula"

`bank-onboarding.md` §7 notes the Model sheet's Master Check needs a real Excel open to
recalculate, which isn't available in this environment. That gap is closed for the
projected years: run

```python
from bizplan.config_loader import load_and_validate
from bizplan.report import data as report_data, validation as report_validation

config = load_and_validate("examples/<institution>/config.py")
computed = report_data.compute(config)
validation = report_validation.validate_model(config, computed["results"])
assert validation["ok"], validation
```

If `validation["ok"]` is `False`, do not proceed to any later pipeline stage — fix the
`config.py` inputs until every projected year's Balance Sheet, Capital Adequacy, and
Liquidity check passes. This mirrors the Model sheet's Master Check exactly (same three
checks, same tolerances) — see `bizplan/report/validation.py`.

## 5. Write `research_output.md`

Same discipline as `bank-onboarding.md` §4 (source + accessed date per datapoint), plus:
record the `as_of` anchor year explicitly at the top of the file, so a reader immediately
knows which vantage point this particular sourcing run represents — this matters once the
same institution has more than one `research_output.md`-worthy run at different anchors.
