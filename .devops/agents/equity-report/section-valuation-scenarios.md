# Section SOP: Valuation, Sensitivity & Scenarios

Read `valuation_inputs.json`. This section **narrates already-computed numbers — it does
not recompute or re-derive any of them.** Every figure must come directly from the JSON.

Write, in order:

1. **The three accounting worlds** (~120 words): name and briefly explain World A (plain
   current-rate method — no inflation restatement, the "disappearing plant" baseline),
   World B (US GAAP temporal method — remeasurement: non-monetary items at historical FX,
   monetary items at current FX, a *remeasurement* gain/loss), and World C (the actual
   IFRS treatment — IAS 29 restatement then IAS 21 translation at the closing rate, what
   the institution really reports). Say plainly that these are three different
   *accounting treatments of the same underlying economics*, not three different
   valuations of the business.
2. **The numbers** (~100 words): state each world's revenue, operating profit, total
   assets, and net monetary/remeasurement gain-or-loss from `scenario_comparison`. **If
   World A and World C diverge sharply on revenue/total assets but only modestly on
   operating profit** (a real pattern this model found — see
   `ias29_impact_primary_year`), say so explicitly and explain why: restating both
   revenue and costs by the same inflation factor largely nets out at the profit line,
   even though the gross revenue/asset figures move a great deal.
3. **IAS 29 impact by subsidiary** (~100 words): narrate `ias29_impact_primary_year`'s
   per-subsidiary total-assets/turnover/operating-profit/net-monetary-gain-loss deltas.
   Name which subsidiary's net monetary result was a gain vs. a loss and, briefly, why
   (see `research_output.md`'s discussion of net monetary position vs. restated-equity
   growth — don't oversimplify to "net monetary liability always means a gain").
4. **2025 validation** (~80 words): state `validation_gap`'s model-vs-disclosed
   comparison plainly, including where it does and does not match in sign. This model's
   own documentation (`research_output.md`) explains why the total-assets line
   structurally can't flip sign here — say so rather than overclaiming a clean match.
5. **Peer comparison** (~90 words, only if `peer_comparison` in the JSON is non-empty):
   briefly note that Coca-Cola FEMSA and BBVA disclose the same kind of IAS 29 effect for
   their own Argentina/Türkiye exposure — cite one concrete figure (e.g. BBVA's
   inflation-linked-bond offset). Then name the real-world regime split worth
   highlighting: Colgate-Palmolive (US GAAP, `peer_comparison.colgate_palmolive`) calls
   the same kind of effect immaterial with no dollar figure disclosed — a real-world
   instance of this model's own "immaterial" conclusion for Unilever, reached
   independently under a different accounting regime — while Reckitt Benckiser (IFRS,
   `peer_comparison.reckitt_benckiser`) discloses it only as a bundled FX-and-
   hyperinflation figure, illustrating that not every IFRS filer matches Unilever's
   disclosure granularity. Keep this short; the point is context, not a full peer
   analysis.

Output plain markdown, no code fences, starting with a `## Valuation, Sensitivity &
Scenarios` heading. Numbers should read naturally in prose, not as a re-typed table (a
table/chart of the same numbers is rendered separately by the PDF-assembly step from the
same JSON).
