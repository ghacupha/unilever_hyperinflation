# Section SOP: Market Consensus Comparison

Read `price_consensus_research.json` and `valuation_inputs.json`. Write ~150-250 words
explicitly comparing this model's own view to "the market's."

- If `consensus_found` is `true`: state the consensus target price/rating and number of
  analysts, then compare it directly to this model's blended fair value
  (`valuation_inputs.json`'s `valuation_per_share.blended`) — state the percentage
  difference and whether this model is more bullish, more bearish, or aligned.
- If `consensus_found` is `false`: **say so plainly — do not imply a consensus exists
  when it doesn't.** State why (e.g. recent listing, thin coverage — see `notes` in the
  JSON), then use `proxy_used` (its description, implied value, and rationale) as the
  stand-in comparison, explicitly labeled as a proxy, not a real consensus.
- Compare the current market **price** itself (not just any consensus/proxy target) to
  this model's blended value, and name the direction and magnitude of any divergence.
- If the JSON's `notes` field flags something specific (e.g. a stale pre-listing report,
  a large price run-up since listing), incorporate it — that context was gathered
  specifically because it matters for this comparison.

Output plain markdown, no code fences, starting with a `## Market Consensus Comparison`
heading.
