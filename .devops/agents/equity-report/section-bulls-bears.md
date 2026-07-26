# Section SOP: Bulls Say / Bears Say

Morningstar's own convention: a short "Bulls Say" list of reasons the stock could
outperform, and an equally serious "Bears Say" list of reasons it could underperform.
Read `valuation_inputs.json` (especially `sensitivity_factors`, `valuation_by_scenario`,
and `financial_health`) and the institution's `research_output.md`.

Write 3-5 bullet points under each heading. Every bullet must ground in something
specific from the data — a sensitivity factor's upside/downside, a scenario spread, a
financial-health sub-grade, a business fact from `research_output.md` (e.g. macro/sector
context, capital trajectory, listing recency). Do not write generic filler ("strong
management team" with nothing behind it).

**This must be genuinely balanced** — real tension between the two lists, not a rubber
stamp of the recommendation. If `recommendation_decision.json`'s signal is "Hold", both
lists should feel roughly equally weighted; don't stack the deck toward whichever
direction you personally find more compelling.

Output plain markdown, no code fences:
```
## Bulls Say
- ...

## Bears Say
- ...
```
