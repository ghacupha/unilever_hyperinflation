# Section SOP: Bulls Say / Bears Say

Morningstar's own convention: a short "Bulls Say" list of reasons the stock could
outperform, and an equally serious "Bears Say" list of reasons it could underperform.
Read `valuation_inputs.json` (especially `scenario_comparison`, `ias29_impact_primary_year`,
and `monetary_exposure`) and the institution's `research_output.md`.

Write 3-5 bullet points under each heading. Every bullet must ground in something
specific from the data — a World A/B/C scenario spread, a subsidiary's IAS 29 impact
figure, a monetary-exposure sub-grade, a business fact from `research_output.md` (e.g.
macro/sector context, a subsidiary's hyperinflationary-since date, the 2025 validation
finding). Do not write generic filler ("strong management team" with nothing behind it).

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
