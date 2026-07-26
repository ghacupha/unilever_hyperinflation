# Section SOP: Price vs. Fair Value & Recommendation

This is the section where the report actually commits to Buy/Hold/Sell. Read
`recommendation_decision.json` — it already contains a **mechanical pre-decision**
(pure arithmetic: price vs. blended fair value, scaled by a valuation-uncertainty tier
using Morningstar's own published margin-of-safety convention). Your job is different
depending on what that mechanical signal already is:

## If `mechanical_signal` is "Buy" or "Sell"

State it and explain the arithmetic plainly (the `rationale` field already has the core
logic — restate it in your own words, don't just copy it verbatim). Make clear this is a
**"regardless of catalyst"** call: the mispricing is large enough, relative to how much
this model's own valuation methods agree with each other, that industry practice (per
Morningstar's published bands) calls for action even without a specific trigger event.
You may still *mention* a plausible catalyst if one exists, but the recommendation does
not depend on finding one.

## If `mechanical_signal` is "Hold" — this is the hard case, read carefully

The mispricing (if any) isn't large enough to act on by arithmetic alone. Your job now is
to look for a **specific, plausible, named catalyst** — a concrete event or development
that could cause the market to re-rate the stock toward (or away from) fair value: a
regulatory change, an earnings report, a macro shift (e.g. interest rate move, election
outcome), a competitive development, a capital raise or listing-related unlock, etc. Use
`valuation_inputs.json`'s `sensitivity_factors` and the institution's `research_output.md`
(macro/sector context) as your source material for plausible catalysts — do not invent
one that isn't grounded in something already in the data.

- **If you can identify a real, specific, named catalyst**: you may argue for overriding
  Hold toward the direction the mispricing implies (`pct_diff`'s sign in
  `recommendation_decision.json` — positive means overvalued/Sell-leaning, negative means
  undervalued/Buy-leaning). Name the catalyst explicitly and explain the mechanism by
  which it would cause a re-rating. Be honest about timing uncertainty — a catalyst
  override should read as a real, falsifiable call, not hedging dressed up as conviction.
- **If you genuinely cannot identify one**: say so directly (e.g. "No specific catalyst
  is identifiable at this time") and confirm the recommendation stays **Hold**. This is
  the expected, honest outcome most of the time — do not manufacture a catalyst just to
  produce a more decisive-sounding recommendation. A fabricated catalyst is worse than an
  honest Hold.

## Format

~200-350 words. State the final recommendation (Buy/Hold/Sell) boldly at the top (e.g.
`**Recommendation: Hold**`), then the reasoning. Output plain markdown, no code fences,
starting with a `## Price vs. Fair Value & Recommendation` heading.
