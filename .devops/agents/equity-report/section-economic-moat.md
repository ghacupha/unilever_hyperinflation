# Section SOP: Economic Moat

Morningstar's own vocabulary: rate the REIT's competitive durability as **Wide**,
**Narrow**, or **None**, then justify it in 150-300 words.

For a REIT specifically, weigh the standard moat sources through that lens:
- **Switching costs** — how sticky are its tenant/anchor-institution relationships (e.g.
  a student-housing REIT's university/college partnerships, a retail REIT's anchor-tenant
  lease terms, long-dated leases with break clauses)? `research_output.md` should have
  the institution's own tenant-concentration and lease-term detail.
- **Cost/scale advantages** — property portfolio scale and diversification vs. peers
  (`peer_reits` in `valuation_inputs.json` gives NAV-discount/premium context;
  `research_output.md` may have occupancy, cost-of-debt, and management-fee-ratio detail),
  weighted-average cost of debt trend, and property-management/operating expertise built
  up over the portfolio's operating history.
- **Regulatory barriers to entry** — CMA REIT authorization (trustee, REIT manager
  licensing, minimum initial-asset thresholds) is itself a barrier industry-wide; note
  this but don't let it alone justify a Wide rating (every authorized REIT has the same
  protection, so it doesn't differentiate this instance from its REIT peers).
- **Brand/trust** — sponsor/promoter track record, length of operating history, listing
  credibility, and (where relevant) a distinctive asset-class specialization that's hard
  for a generalist competitor to replicate (e.g. purpose-built student accommodation vs.
  generic office/retail).

Read `research_output.md` for the institution's own specifics and `valuation_inputs.json`'s
`peer_reits` list for relative positioning. Be honest about a **None** or **Narrow**
rating where warranted — a REIT in a competitive, undifferentiated property segment with
no discernible cost or switching-cost advantage over its peers does not automatically
deserve a Wide moat just because it holds real estate.

Output plain markdown, no code fences, starting with a `## Economic Moat` heading and a
bold one-line rating (`**Moat Rating: Narrow**` or equivalent) before the justification.
