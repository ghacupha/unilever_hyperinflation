# Section SOP: Market Consensus Comparison

Read `price_consensus_research.json` and `valuation_inputs.json`. Write ~150-250 words
explicitly comparing this model's own quantified view (the IAS 29 impact and monetary
gain/loss figures) to how "the market" actually talks about it.

- If `consensus_found` is `true`: state what real analyst/sell-side commentary actually
  says about the hyperinflationary subsidiaries — quote or closely paraphrase the
  specific language found. Then say plainly whether that commentary **distinguishes the
  IAS 29 net monetary gain/(loss) from ordinary FX translation**, or folds it into
  generic "FX headwind" language without separating the two. This distinction is the
  whole point of the comparison — don't just summarize consensus generically.
- If `consensus_found` is `false`: **say so plainly — do not imply consensus commentary
  exists when it doesn't.** State why (see `notes` in the JSON), then use `proxy_used`
  (its description and rationale) as the stand-in, explicitly labeled as a proxy.
- Compare that read against this model's own `ias29_impact_primary_year` and
  `monetary_exposure` figures from `valuation_inputs.json` — is the real-world commentary
  proportionate to the size of the effect this model computes, understating it, or
  overstating it?
- If the JSON's `notes` field flags something specific, incorporate it — that context was
  gathered specifically because it matters for this comparison.

Output plain markdown, no code fences, starting with a `## Market Consensus Comparison`
heading.
