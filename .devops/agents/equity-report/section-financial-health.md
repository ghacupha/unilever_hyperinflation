# Section SOP: Financial Health

Read `valuation_inputs.json`'s `monetary_exposure` object. **The grades are already
computed — narrate them, do not assign your own.** It's a simple, documented rule
(|net monetary gain/loss| ÷ total assets, banded A-F; overall grade = the worst of the
per-subsidiary sub-grades) — say so plainly rather than implying a more sophisticated
methodology than what was actually used.

Write ~150-250 words:
- State the overall letter grade and each subsidiary's own sub-grade, with the underlying
  net monetary gain/(loss) and total-assets figures and exposure ratio each is measured
  against.
- If one subsidiary's grade is notably weaker than the other, say which one is dragging
  the overall grade down and why that matters for the investment case. **A weak grade is
  a real balance-sheet-discipline signal, not a technicality** — it means that
  subsidiary's net monetary position (cash/receivables vs. payables/debt) is large enough
  relative to its total assets that ordinary inflation materially erodes or inflates its
  real value each period, and that's worth stating plainly rather than softening.
- Note this reflects the **primary calibrated year** (`ias29_impact_primary_year`'s
  `year` field in `valuation_inputs.json`, 2024 for Unilever) — the year the model's
  local-currency inputs were solved to reproduce the institution's real disclosed figures
  — not the rolled-forward validation year, which is a directional check, not a current-
  state snapshot.

Output plain markdown, no code fences, starting with a `## Financial Health` heading and
the overall grade stated boldly up front (e.g. `**Overall Grade: C**`).
