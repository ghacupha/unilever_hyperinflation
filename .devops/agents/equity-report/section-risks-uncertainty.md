# Section SOP: Risks & Uncertainty

Write ~150-300 words on what could make this thesis wrong, in either direction. Ground
every risk in something specific rather than generic ("execution risk", "market risk"
with nothing behind them):

- The 3 `sensitivity_factors` in `valuation_inputs.json` are themselves risk factors —
  name them and their downside magnitude explicitly (e.g. "a sustained occupancy decline
  would cut average Net Profit by roughly X%").
- The valuation-method spread (`method_values`/`uncertainty_tier` in
  `recommendation_decision.json`) is itself a form of uncertainty worth naming plainly —
  a wide spread between NAV/DDM/Cap Rate means real disagreement about what this
  property portfolio is worth, not just noise.
- Macro/regulatory risks specific to this instance's market from `research_output.md`
  (e.g. election-cycle uncertainty, CMA gearing/distribution rule changes, sector
  cap-rate or occupancy trends, currency risk for a USD-denominated REIT) — cite what's
  actually there, don't invent generic country risk.
- If the institution is recently listed (check `price_consensus_research.json`'s notes),
  say so explicitly as its own uncertainty factor — thin trading history and absent
  analyst coverage are real limitations on how much confidence to place in any single
  valuation figure, this model's included.

Output plain markdown, no code fences, starting with a `## Risks & Uncertainty` heading.
