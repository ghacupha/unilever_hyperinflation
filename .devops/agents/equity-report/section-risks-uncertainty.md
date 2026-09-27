# Section SOP: Risks & Uncertainty

Write ~150-300 words on what could make this thesis wrong, in either direction. Ground
every risk in something specific rather than generic ("execution risk", "market risk"
with nothing behind them):

- The monetary-exposure grades (`monetary_exposure` in `valuation_inputs.json`) are
  themselves risk factors — name the weakest-graded subsidiary and its exposure ratio
  explicitly (e.g. "Argentina's net monetary position is roughly X% of its total assets —
  a further inflation shock or FX move erodes/inflates that position directly").
- **Model-limitation risk, stated plainly**: this is a calibrated illustrative model, not
  a reproduction of the institution's actual subsidiary financial statements (see
  `research_output.md`'s "What this model is and isn't"). The 2025 validation pass
  matched sign on 3 of 4 lines per subsidiary but not magnitude, and the total-assets line
  structurally can't reproduce a negative disclosed impact under this model's mechanics —
  say so as a real limit on how much confidence to place in any *forward* projection from
  this model, as distinct from its 2024 calibration (which does match closely).
- Macro/regulatory risks specific to each subsidiary's market from `research_output.md`
  (e.g. Argentina's 2025 currency float reversing the inflation-vs-FX relationship that
  drove 2024's results, Türkiye's continued lira depreciation) — cite what's actually
  documented there, don't invent generic country risk.
- If real analyst consensus (check `price_consensus_research.json`'s notes) doesn't
  distinguish the IAS 29 effect from ordinary FX noise, say so explicitly as its own risk
  — a market that doesn't price a real, quantified effect correctly is a source of
  potential mispricing in either direction, not just a data-quality footnote.
- **Classification risk, if `standard_setting_note` in `valuation_inputs.json` is
  non-empty**: cite it briefly — a subsidiary's hyperinflationary classification rests
  on qualitative judgment across several IAS 29.3 indicators, not a single bright-line
  inflation number (the IFRS Interpretations Committee confirmed this in a July 2025
  agenda decision). A future reclassification either way (e.g. if Türkiye's easing
  inflation eventually tips the qualitative assessment) would remove or add this entire
  effect, not just shrink or grow it.

Output plain markdown, no code fences, starting with a `## Risks & Uncertainty` heading.
