# Section SOP: Financial Health

Read `valuation_inputs.json`'s `financial_health` object. **The grade is already
computed — narrate it, do not assign your own.** It's a simple, documented rule (buffer
above the regulatory minimum for capital/liquidity; absolute bands for the NPL ratio;
overall grade = the worst of the three sub-grades) — say so plainly rather than
implying a more sophisticated methodology than what was actually used.

Write ~150-250 words:
- State the overall letter grade and the three sub-grades (capital, liquidity, asset
  quality/NPL) with their underlying ratios and the regulatory minimums they're measured
  against.
- If any sub-grade is notably weaker than the others (as it commonly will be — capital
  and liquidity buffers tend to look strong against CBK minimums while NPL/asset quality
  is the more binding constraint), say which one is dragging the overall grade down and
  why that matters for the investment case.
- Note this reflects the **nearest projected year**, not a long-run average — financial
  health can and does drift across the projection horizon (`capital`/`liquidity` in
  `valuation_inputs.json` are indexed by year if a longer view is useful).

Output plain markdown, no code fences, starting with a `## Financial Health` heading and
the overall grade stated boldly up front (e.g. `**Overall Grade: C**`).
