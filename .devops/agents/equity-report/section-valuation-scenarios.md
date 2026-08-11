# Section SOP: Valuation, Sensitivity & Scenarios

Read `valuation_inputs.json`. This section **narrates already-computed numbers — it does
not recompute or re-derive any of them.** Every figure must come directly from the JSON.

Write, in order:

1. **Valuation methodology** (~100 words): name the three methods (NAV, Dividend Discount
   Model, Direct Capitalization/cap rate) and the blend weights (`blend_weights` — e.g.
   "40% NAV / 30% DDM / 30% Cap Rate, reflecting NAV as the primary anchor for a
   property-holding entity — the most reliable value driver when the underlying assets
   are independently appraised — with DDM and direct capitalization as cross-checks").
   Note the DDM here is a dividend-plus-terminal-NAV hybrid, not a pure Gordon-growth
   annuity: with REIT payout ratios often well below 100%, most of the total return
   accrues through NAV growth on retained earnings, not distributions alone.
2. **The numbers** (~80 words): state each method's per-unit value
   (`valuation_per_unit`) and the blended figure. **If the methods diverge
   significantly** (e.g. more than ~50% spread between the highest and lowest), say so
   explicitly and note what that implies about valuation uncertainty — don't paper over
   a wide spread by only quoting the blended number.
3. **Net Profit sensitivity** (~100 words): narrate the 3 factors in
   `sensitivity_factors` (name, category, downside/upside % impact on average Net
   Profit). State which single factor has the largest swing.
4. **Scenario comparison** (~80 words): compare `valuation_by_scenario`'s Base/Best/Worst
   blended-per-unit values, and note the spread between Best and Worst as a plain
   statement of projection uncertainty.

Output plain markdown, no code fences, starting with a `## Valuation, Sensitivity & Scenarios`
heading. Numbers should read naturally in prose, not as a re-typed table (a table of the
same numbers is rendered separately by the PDF-assembly step from the same JSON).
