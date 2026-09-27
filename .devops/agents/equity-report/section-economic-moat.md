# Section SOP: Economic Moat

Morningstar's own vocabulary: rate the institution's competitive durability as **Wide**,
**Narrow**, or **None**, then justify it in 150-300 words — with this report's specific
lens: does the institution's brand/pricing power hold up *inside* a hyperinflationary
market, or does operating there expose a currency/margin mismatch that erodes the moat
locally even if the global brand itself is strong?

Weigh the standard moat sources through that lens:
- **Pricing power / switching costs** — can the institution raise local prices roughly
  in line with local inflation (protecting real revenue) or does it lag, showing up as
  margin compression? `research_output.md`'s discussion of each subsidiary's business
  and `valuation_inputs.json`'s `scenario_comparison` (World A vs. World C operating
  profit) give a quantified read on this — a large gap between the two worlds' operating
  profit isn't itself a moat signal, but the *underlying margin trend* it's built on is.
- **Cost/scale advantages** — global sourcing/manufacturing scale that a purely local
  competitor can't match, and whether that scale advantage survives local FX/inflation
  disruption or gets diluted by it.
- **Monetary-exposure discipline** — `valuation_inputs.json`'s `monetary_exposure` grades
  are a direct, quantified read on balance-sheet discipline in a hyperinflationary market:
  a subsidiary holding large net monetary *assets* (cash trapped by capital controls, for
  instance) bleeds real value every period inflation runs; a well-managed local treasury
  function keeps net monetary exposure small. Cite the grade and exposure ratio for each
  subsidiary explicitly.
- **Brand/trust** — global brand equity and the institution's own track record of
  operating through prior hyperinflationary episodes (`research_output.md`'s
  hyperinflationary-since dates for each subsidiary are relevant here — a subsidiary
  hyperinflationary since 2018 has more institutional experience managing it than one
  only since 2022).

Read `research_output.md` for the institution's own specifics and `valuation_inputs.json`
for the quantified inputs above. Be honest about a **None** or **Narrow** rating for a
specific *subsidiary's* local operating environment even where the *global* brand
clearly carries a wide moat elsewhere — the two questions are separate, and this section
should distinguish them rather than let a strong global brand paper over a genuinely
exposed local position.

Output plain markdown, no code fences, starting with a `## Economic Moat` heading and a
bold one-line rating (`**Moat Rating: Narrow**` or equivalent) before the justification.
