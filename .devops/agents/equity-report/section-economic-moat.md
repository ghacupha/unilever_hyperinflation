# Section SOP: Economic Moat

Morningstar's own vocabulary: rate the institution's competitive durability as **Wide**,
**Narrow**, or **None**, then justify it in 150-300 words.

For a bank specifically, weigh the standard moat sources through that lens:
- **Switching costs** — how sticky are its deposit/customer relationships (branch/agent
  network reach, digital-channel lock-in, payroll/salary-account relationships)?
- **Cost/scale advantages** — deposit funding cost vs. peers (`peer_banks` in
  `valuation_inputs.json` gives ROAE/payout context; `research_output.md` may have cost-
  to-income and NIM detail), branch/agent network scale.
- **Regulatory barriers to entry** — banking licenses are themselves a barrier industry-
  wide; note this but don't let it alone justify a Wide rating (every peer has the same
  protection, so it doesn't differentiate this institution from them).
- **Brand/trust** — long operating history, market position, ownership/listing
  credibility.

Read `research_output.md` for the institution's own specifics and `valuation_inputs.json`'s
`peer_banks` list for relative positioning. Be honest about a **None** or **Narrow**
rating where warranted — a recently-listed, mid-sized bank in a competitive market with
no discernible cost or switching-cost advantage over its peers does not automatically
deserve a Wide moat just because it's a bank.

Output plain markdown, no code fences, starting with a `## Economic Moat` heading and a
bold one-line rating (`**Moat Rating: Narrow**` or equivalent) before the justification.
