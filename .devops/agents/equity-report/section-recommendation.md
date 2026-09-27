# Section SOP: Recommendation

This is the section where the report commits to a call — but this model doesn't build a
full DCF/multiples equity valuation (out of scope; this project is about the
hyperinflation *accounting* mechanics, not a from-scratch Unilever valuation). So the
call this section makes is narrower and specific: **is the market's treatment of the
hyperinflation effect itself a source of mispricing?** Read `recommendation_decision.json`
(the mechanical materiality flag: is the net monetary gain/(loss) large enough relative
to group operating profit to matter — see `bizplan/report/recommendation.py`'s module
docstring) and `price_consensus_research.json` (does real analyst consensus separate this
effect from ordinary FX, or fold it into generic noise).

## Decision logic

Combine the two mechanical/researched inputs like this — state your reasoning, don't just
assert the conclusion:

- **`mechanical_signal` is "Flag: immaterial"**: the effect doesn't move group-level
  numbers enough to justify a directional call either way, regardless of how consensus
  treats it. **Recommendation: Hold** on this specific question — there's no
  informational edge to act on here, whatever the market believes.
- **`mechanical_signal` is "Flag: material" AND consensus/market commentary explicitly
  and correctly separates the effect** (per Stage 2's research): the risk is real but
  already priced in. **Recommendation: Hold** — no edge, but for a different reason than
  above (state which reason applies).
- **`mechanical_signal` is "Flag: material" AND consensus does NOT distinguish it from
  ordinary FX** (folds it into generic "FX headwind" commentary, or ignores it): this is
  the case where a real, quantified, structural effect isn't being priced correctly.
  **Recommendation: Sell-leaning / Caution** if the effect has been a net drag (net
  monetary loss, or a subsidiary trending toward a bigger loss per the 2025 validation
  direction) that consensus underweights; **Buy-leaning** if it's been a net gain
  consensus underweights. State which subsidiary is driving this (`worst_exposure_subsidiary`
  in `recommendation_decision.json`) and be explicit that this is a call about
  *earnings-quality mispricing*, not a full intrinsic-value target price.
- **If Stage 2 found no real consensus commentary at all** (`consensus_found: false` in
  `price_consensus_research.json`): say so directly and default to **Hold** — there's no
  basis to claim the market is mispricing something you can't observe the market's view
  of. Do not manufacture a market view to force a more decisive-sounding call.

## Format

~200-350 words. State the final call boldly at the top (e.g. `**Recommendation: Hold**`),
then the reasoning tracing through the decision logic above. Output plain markdown, no
code fences, starting with a `## Recommendation` heading.
