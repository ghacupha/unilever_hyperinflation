# Section SOP: Financial Health

Read `valuation_inputs.json`'s `financial_health` object. **The grade is already
computed — narrate it, do not assign your own.** It's a simple, documented rule (buffer
above/below the CMA regulatory minimum for LTV/income-producing-%/payout; overall grade
= the worst of the three sub-grades) — say so plainly rather than implying a more
sophisticated methodology than what was actually used.

Write ~150-250 words:
- State the overall letter grade and the three sub-grades (LTV/gearing, income-producing
  real estate %, distribution payout) with their underlying ratios and the CMA minimums/
  maximums they're measured against.
- If any sub-grade is notably weaker than the others, say which one is dragging the
  overall grade down and why that matters for the investment case. **A weak payout grade
  is a real governance signal, not a technicality** — the CMA requires I-REITs to
  distribute at least 80% of taxable income; a REIT paying out materially less (even while
  its gearing and asset-mix ratios look strong) is retaining cash rather than returning it
  to unit-holders as required, and that's worth stating plainly rather than softening.
- Note this reflects the **latest actual (disclosed) year**, not a projected year —
  financial health here is a statement of current, real, filed fact
  (`nav_per_unit_series`/`net_profit_series` in `valuation_inputs.json` give a longer
  year-by-year view if useful).

Output plain markdown, no code fences, starting with a `## Financial Health` heading and
the overall grade stated boldly up front (e.g. `**Overall Grade: C**`).
