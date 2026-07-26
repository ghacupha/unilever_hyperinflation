# Section SOP: Valuation, Sensitivity & Scenarios

Read `valuation_inputs.json`. This section **narrates already-computed numbers — it does
not recompute or re-derive any of them.** Every figure must come directly from the JSON.

Write, in order:

1. **Valuation methodology** (~100 words): name the three methods (DDM, Residual
   Income/Excess Return, P/B-ROE regression) and the blend weights
   (`blend_weights` — e.g. "50% DDM / 30% RI / 20% P/B-ROE, reflecting DDM as the primary
   method and RI as a cross-check for banks specifically, per Damodaran's own framework
   for financial-service-firm valuation").
2. **The numbers** (~80 words): state each method's per-share value
   (`valuation_per_share`) and the blended figure. **If the methods diverge
   significantly** (e.g. more than ~50% spread between the highest and lowest), say so
   explicitly and note what that implies about valuation uncertainty — don't paper over
   a wide spread by only quoting the blended number.
3. **Net Income sensitivity** (~100 words): narrate the 3 factors in
   `sensitivity_factors` (name, category, downside/upside % impact on average PAT). State
   which single factor has the largest swing.
4. **Scenario comparison** (~80 words): compare `valuation_by_scenario`'s Base/Best/Worst
   blended-per-share values, and note the spread between Best and Worst as a plain
   statement of projection uncertainty.

Output plain markdown, no code fences, starting with a `## Valuation, Sensitivity & Scenarios`
heading. Numbers should read naturally in prose, not as a re-typed table (a table of the
same numbers is rendered separately by the PDF-assembly step from the same JSON).
