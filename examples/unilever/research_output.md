# Research Output — Unilever plc Hyperinflation Model (Argentina & Türkiye)

Calibration and citation log for `config.py`. This is a working research log, not a
substitute for the model itself — see `BLUEPRINT.md` for the full design.

## What this model is and isn't

Unilever plc reports under IFRS and applies **IAS 29** to its Argentina (hyperinflationary
since 1 Jul 2018) and Türkiye (since 1 Jul 2022) operations, then translates the restated
figures under **IAS 21** at the closing rate. It discloses, each year, the aggregate impact
of that treatment on consolidated Total assets, Turnover, Operating profit, and Net
monetary gain/(loss) — but not the underlying subsidiary financial statements at a level
of detail that would let anyone reconstruct the restatement mechanically.

So this model does **not** reproduce Unilever's actual Argentina/Türkiye subsidiary
accounts. It builds a small, fully hand-traceable fictional subsidiary for each, sized so
that running it through the model's IAS 29 + IAS 21 engine (`bizplan/financial/
hyperinflation_calculations.py`) reproduces Unilever's own **real disclosed 2024** impact
figures — the primary calibration target — almost exactly, then rolls the same model
forward into **2025** with updated (not re-solved) macro assumptions as an out-of-sample
validation against the real 2025 disclosure. `config.py`'s docstring and inline comments
repeat this; it's worth saying once more here in full.

## Real disclosed figures (calibration target and validation target)

| IAS 29 impact, €m | 2024 Argentina | 2024 Türkiye | 2024 Total | 2025 Argentina | 2025 Türkiye | 2025 Total |
|---|---:|---:|---:|---:|---:|---:|
| Total assets | +474 | +65 | +539 | −199 | −20 | −219 |
| Turnover | +230 | +187 | +417 | −90 | −16 | −106 |
| Operating profit | +10 | −4 | +6 | −54 | −46 | −100 |
| Net monetary gain/(loss) | −206 | +11 | −195 | −46 | −10 | −56 |

Sources: Unilever plc Form 20-F for FY2024 and FY2025 (both filed with the SEC), the
hyperinflation accounting policy note. See `config.py`'s `SOURCES` for URLs.

## Calibration method (2024)

The engine's restatement math is linear enough in the local-currency inputs to solve
backward from the four EUR targets algebraically, rather than by trial and error:

1. **Turnover and operating-profit impact** fix the subsidiary's revenue and operating
   profit level under World A (plain current-rate, no restatement) — because, under the
   model's simplifying assumption that revenue/COGS/opex/depreciation are all restated
   by the same in-year "flow" factor, `Impact = Level_A × (r − 1)`, where `r` is the ratio
   of the inflation-restatement factor to the FX-depreciation factor over the year. Given
   `r` (fixed once the year's inflation index and FX path are chosen) and the target
   impact, `Level_A` — and hence the required local-currency revenue/cost figures — falls
   out directly.
2. **Total-assets impact** is driven purely by the non-monetary-asset restatement (opening
   non-monetary assets × the full-year inflation factor, plus in-year capex restated by
   the flow factor, less restated depreciation) — it turns out to be **independent of the
   net monetary position** in this model, so it's solved as a second, separate linear
   equation for the opening non-monetary asset balance.
3. **Net monetary gain/(loss)** is computed as the balancing plug that makes the restated
   balance sheet tie out (`restated assets − restated liabilities − restated opening
   equity − restated operating profit`). With the non-monetary-asset restatement already
   fixed by step 2, and opening equity fixed as a modeling choice, the plug equation is
   linear in the net monetary position (monetary assets minus monetary liabilities), which
   is solved for directly, then split into a plausible cash/receivables-vs-payables/debt
   pair.

Both subsidiaries hit all four 2024 targets to within model precision (Argentina:
+474.0/+230.0/+10.0/−206.0 exactly; Türkiye: +65.0/+187.0/−4.0/+11.0 exactly). **Opening
equity and the individual monetary-asset/liability split are the two genuinely free
modeling choices** in this calibration — not derived from any disclosure — chosen to
produce a plausible balance sheet shape, not to hit a target (no public target exists for
them). Everything else was solved, not guessed.

### A finding worth flagging: the naive CFA heuristic doesn't fully hold here

The common CFA-curriculum intuition — "net monetary liability position → purchasing-power
*gain*; net monetary asset position → *loss*" — holds exactly only in a single-item, static
setting. In this full model, Argentina's solved net monetary position comes out as a
**liability** position (~ARS 407bn), yet the subsidiary still shows a **net monetary
loss** (−206). That's because the plug also nets against the *growth* of the other
restated items (opening equity and operating profit, both scaled up by inflation) — a
fast-growing restated equity/profit base can turn what looks like a "monetary liability =
gain" setup into a net loss once the whole balance sheet is restated together, not just the
monetary line in isolation. Worth surfacing explicitly when teaching this reading: the
simple heuristic is a starting intuition, not a formula that survives a full consolidated
restatement.

## 2025 roll-forward validation — a documented, partial match

2025 was **not** re-solved to fit the real 2025 table. Instead, `config.py`'s 2025
`ACTUALS` roll the 2024 model forward mechanically:

- Non-monetary assets and equity carry forward from the model's own **2024 IAS29-restated
  closing local-currency balances** (via `restated_closing_local()`), consistent with how
  an ongoing hyperinflationary entity's opening balance is always the prior year's already-
  restated closing figure.
- Revenue/costs grow with local inflation (zero assumed real growth), except Türkiye's
  costs, where a modest margin-recovery assumption (costs growing slower than revenue) was
  applied — see below for why.
- The macro path itself changes deliberately: **2024's actual relationship — local
  inflation (118% Argentina / 44% Türkiye) outpacing FX depreciation (~19% / ~18%, both
  currencies under managed/crawling regimes) — is exactly what produced positive 2024
  impacts.** For 2025, both currencies' real-world FX regimes changed materially
  (Argentina floated the peso in April 2025, ending its crawling peg; Türkiye's lira
  continued depreciating while disclosed inflation kept decelerating), plausibly
  *reversing* that relationship. The model's 2025 macro assumptions (inflation
  decelerating to ~30%/~28%, FX depreciation accelerating to ~44%/~35%) encode that
  reversal.

**Result — same-sign match on 3 of 4 lines for each subsidiary, total-assets sign not
reproduced:**

| | Argentina model | Argentina real | Türkiye model | Türkiye real |
|---|---:|---:|---:|---:|
| Total assets | +183.7 | −199 | +46.1 | −20 |
| Turnover | −31.3 | −90 | −47.4 | −16 |
| Operating profit | −1.4 | −54 | −3.3 | −46 |
| Net monetary gain/(loss) | −23.8 | −46 | −113.3 | −10 |

Turnover, operating profit, and net monetary gain/loss all correctly flip to the real
disclosed sign (negative) for both subsidiaries once FX depreciation is assumed to
outpace inflation in 2025 — the same mechanism that produced 2024's positive figures,
run in reverse. Magnitudes are the right order of magnitude for Argentina, overshoot for
Türkiye's net monetary line, and undershoot for both subsidiaries' operating-profit lines
— a real, acknowledged gap, not smoothed over.

**Total-assets impact never flips sign in this model, structurally.** The formula
(`[nonmon_open×(inflation factor−1) + capex×(flow factor−1) − restated depreciation
increase] ÷ closing FX`) has a positive numerator whenever the price index is rising —
which, in a hyperinflationary economy, it always is — regardless of how much FX
depreciates, because both World A and World C divide by the *same* closing FX rate for
balance-sheet items. Pure inflation restatement of non-monetary assets can only ever raise
their local-currency value; it cannot make the asset-restatement impact negative. Real
Unilever's negative 2025 total-assets impact therefore almost certainly reflects something
this simplified single-period model doesn't capture from the four-line summary table alone
— e.g., disposals/impairments recognized alongside the restatement, or a comparative-basis
convention in Unilever's own note that isn't evident without the full note text (which
wasn't available to this research pass, only the headline table). **This is flagged as an
open limitation, not resolved** — and is itself a good discussion point for the CFA
reading: the definition of the comparative baseline matters as much as the restatement
mechanics.

## Why Türkiye 2025 assumes margin recovery

Türkiye's 2024 World-A (un-restated) operating profit came out as a **loss** (~−€38m on
~€1.78bn World-A revenue) from the 2024 calibration. Under the model's proportional
restatement logic, `Impact = Level_A × (r − 1)`: with `r` now below 1 (2025's reversed
macro path), a *negative* `Level_A` times a *negative* `(r−1)` gives a **positive**
impact — the wrong sign. Assuming Türkiye's underlying business recovers to a modest
operating profit in 2025 (a real, plausible outcome — Unilever and peers raised local
prices and cut costs through 2024-2025 specifically to rebuild Turkish-lira margins) flips
`Level_A` positive, which is what's needed for a negative `(r−1)` to produce the
disclosed-matching negative operating-profit impact. This is a modeling choice made
explicitly to test the mechanism, not a disclosed fact about Unilever Türkiye's real 2025
margin.

## Item classification (CFA teaching reference)

See `config.py`'s `ITEM_CLASSIFICATION` for the monetary/non-monetary/IAS29-treatment/
translation table (cash, receivables, inventory, PPE, payables, debt, share capital,
revenue, COGS, depreciation) — this is a reference table for the model's Assumptions
sheet, not fed into the calculation engine directly (which works off subsidiary-level
aggregates: total non-monetary assets, total monetary assets, total monetary
liabilities).

## Market perception — confirmed (live research, 2026-09-27)

Stage 2 of the report pipeline (`bizplan/report/price_research.py`) ran live and
confirmed the hypothesis this whole report is built around. Across Unilever's Q1 and Q2
2026 earnings-call transcripts and public analyst/aggregator commentary (TipRanks,
MarketScreener, MarketBeat), Argentina and Türkiye come up only as volume/growth stories
plus a generic aggregate "currency headwind" to reported turnover and underlying EPS —
e.g. CFO Srinivas Phatak, Q2 2026: *"Currency reduced our first half turnover by
4.9%... Currency reduced the underlying EPS growth by around 6 percentage points in the
first half."* No sell-side note, analyst question, or press summary found separates the
IAS 29 net monetary gain/(loss) from ordinary FX translation. Unilever's own USG
(underlying sales growth) methodology instead **caps hyperinflationary price growth out
of the metric entirely** rather than presenting the net monetary line as a distinct
purchasing-power effect. Limitation, stated plainly by the research itself: paywalled
broker notes (Deutsche Bank, Barclays, Bernstein) weren't accessible, so this rests on
public transcripts and aggregator summaries only. Reconfirmed, independently, on two
further live runs since (`BACKLOG.md` Phase 7's extension and Phase 12) — the second
pass additionally found a Jefferies analyst using the word "hyperinflation" directly on
the Q2 2026 call, but only in a question about pricing, never about the monetary line.
Full finding with every citation:
`examples/2026-09-28_204838/report_workdir/price_consensus_research.json` (the latest
live pipeline run's own output).

## Peer comparison — this pattern isn't unique to Unilever

Four other multinationals disclose (or explicitly decline to quantify) the same kind of
hyperinflation effect for their own Argentina/Türkiye exposure — cited in `config.py`'s
`PEER_COMPARISON`, not built into this model's own engine (no subsidiary reconstruction
attempted for any of them):

- **Coca-Cola FEMSA** (Argentina, hyperinflationary since 1 Jan 2018): its H1 2025 net
  monetary position *gain* rose to Ps.154m from Ps.42m in H1 2024, driven mainly by
  Argentine liabilities benefiting from inflation — a textbook "net monetary liability →
  gain" case. Worth contrasting directly with Unilever's own Argentina, which is *also*
  a net monetary liability position (see "A finding worth flagging" above) yet still
  books a net *loss* — the same starting condition, opposite outcome, because Unilever's
  restated equity/profit growth outweighs the liability's real-value erosion while
  FEMSA's apparently doesn't (or does so less). Source: Coca-Cola FEMSA Form 20-F FY2025
  ([SEC EDGAR](https://www.sec.gov/Archives/edgar/data/910631/000162828026025313/kof-20251231.htm)).
- **BBVA** (Türkiye, via Garanti BBVA, hyperinflationary since 1 Jan 2022) discloses a
  net monetary loss *and* a separate, partially offsetting inflation-linked-bond
  revaluation gain each year: FY2023 −€2,118m / +€1,202m; FY2022 −€2,323m / +€1,490m.
  The inflation-linked bonds are treated under IAS 29 as "protective assets" — a real
  hedge against the same purchasing-power erosion this model's illustrative subsidiaries
  don't hold. This model's World A/B/C engine has no equivalent instrument — a real,
  acknowledged simplification (see "Known simplifications" below), not fixed in this
  pass. A full BBVA/Garanti subsidiary-level reconstruction (Garanti publishes its own
  full IFRS statements, unlike Unilever) stays deferred as `BACKLOG.md` Phase 5. Source:
  BBVA Form 20-F FY2023
  ([SEC EDGAR](https://www.sec.gov/Archives/edgar/data/842180/000084218024000007/bbva-20231231.htm)).

### Two more peers — a real-world IFRS-vs-US-GAAP natural experiment, and a disclosure-granularity contrast

The first two peers above are, like Unilever, IFRS filers applying IAS 29. Household/
personal-care goods companies split along a real accounting-regime line worth citing
directly, since it's exactly the World B/World C choice this model's engine simulates
synthetically — here it's two real companies actually making that choice in production:

- **Colgate-Palmolive** (US GAAP filer — real-world **World B**, not a synthetic
  comparison): its 10-K names Argentina, Türkiye, *and Nigeria* as "highly inflationary"
  under ASC 830 (the US GAAP equivalent of this model's temporal method), and states
  plainly that the designation **"has not had and is not expected to have a material
  impact on the Company's Consolidated Financial Statements."** No dollar figure is
  disclosed — precisely because management judges the effect immaterial. This is a
  real-world instance of the exact qualitative conclusion this model's own Stage 3
  reaches for Unilever (`recommendation_decision.json`'s `"Flag: immaterial"`), reached
  independently, under a different accounting regime, with no quantified model behind
  it. Worth noting too: Colgate names *Nigeria* as hyperinflationary, which doesn't
  appear on EY's April 2026 list (see "Standard-setting watch" below) — a live example
  of different companies exercising different judgment on a borderline economy, exactly
  the kind of variation the IFRS Interpretations Committee's July 2025 agenda decision
  was asked to weigh in on. Source: Colgate-Palmolive Form 10-K FY2025
  ([SEC EDGAR](https://www.sec.gov/Archives/edgar/data/21665/000002166526000006/cl-20251231.htm)).
- **Reckitt Benckiser** (IFRS filer — same regime as Unilever, but a real illustration
  that not every IFRS filer discloses IAS 29 impact with Unilever's granularity):
  Reckitt's 2025 Annual Report and Accounts doesn't carry a separate net-monetary-
  gain/(loss) line at all — FX translation and hyperinflation are bundled into one
  "Exchange and hyperinflation" reconciling item for its like-for-like revenue measure
  (£394m impact in 2025, up from £24m in 2024 — not separable into the two effects from
  what's disclosed). More strikingly, Reckitt **fully divested its Argentina business on
  31 December 2025**, bundled into a £2.2bn sale of its "Essential Home" segment
  (factories in the UK, Argentina, Spain, Portugal, Hungary, and Mexico all sold
  together) — so its only remaining hyperinflation exposure going forward is Türkiye.
  Read directly from Reckitt's own Financial Statements PDF, not a secondary summary.
  Source: Reckitt Benckiser Annual Report and Accounts 2025
  ([reckitt.com](https://www.reckitt.com/investors/latest-annual-report/)).

## Standard-setting watch — why Türkiye still counts as hyperinflationary

The IFRS Interpretations Committee published a July 2025 agenda decision, *Assessing
Indicators of Hyperinflationary Economies*, concluding that companies should weigh **all**
of IAS 29.3's qualitative indicators — price-indexation prevalence, wage-linking, public
trust in the local currency, interest/inflation-rate relationships — not just the
>100%/3-year cumulative-inflation rule most people treat as the sole test. The Committee
found little diversity in how stakeholders already apply this and did not add a
standard-setting project (i.e., current practice stands). This is directly relevant here:
Türkiye's headline annual inflation has eased toward ~31% (2026,
[Trading Economics](https://tradingeconomics.com/turkey/inflation-cpi)) — well under the
naive >100%/3yr threshold — yet it remains on
[EY's current hyperinflationary-economies list](https://www.ey.com/en_lt/technical/ifrs-technical-resources/hyperinflationary-economies-updated-april-2026)
(Argentina, Türkiye, Haiti, Iran, Lebanon, Malawi, South Sudan, Sudan, Venezuela,
Zimbabwe, as of April 2026) on the qualitative indicators. Source:
[IFRS Interpretations Committee, July 2025 agenda decision](https://www.ifrs.org/projects/completed-projects/2025/assessing-indicators-of-hyperinflationary-economies-IAS-29/).

## Known simplifications

- **Single aggregate non-monetary bucket** (inventory + PPE combined) per subsidiary,
  rather than item-level restatement with separate acquisition-date vintages for
  inventory (recent) vs. PPE (older). A real IAS 29 restatement would restate PPE by a
  much larger multiplier (older historical cost) than inventory (recent purchases) — this
  model's single geometric-mean "flow" factor for in-year additions and a single "opening"
  factor for the whole opening non-monetary balance is a simplification for
  hand-traceability, at the cost of item-level precision.
- **Geometric-mean average index/FX** (`√(open × close)`) stands in for a full monthly
  series, per the same hand-traceability goal — a real subsidiary would restate each
  month's transactions by that month's index, not a single blended annual average.
- **Depreciation restated at the same "flow" factor as opex**, rather than at each
  underlying asset's own historical acquisition-date index — a further simplification of
  the same kind.
- **Opening equity and the monetary-asset/liability split are free modeling choices**
  (see "Calibration method" above) — not derived from any Unilever disclosure.
- **`OTHER_GROUP_OPERATIONS_EUR`** (the non-hyperinflationary rest of the group) is an
  illustrative scale, not Unilever's real consolidated ex-Argentina/Türkiye figures —
  which is also why the 2.3% materiality ratio in `recommendation_decision.json` is
  indicative only, not computed against Unilever's actual reported group operating
  profit (a real finding the live pipeline's own coherence gate caught — see
  `BACKLOG.md` Phase 4).
- **No inflation-linked-bond (or other protective-asset) modeling** — unlike BBVA's real
  disclosed Türkiye treatment (see "Peer comparison" above), this model's illustrative
  subsidiaries hold no instrument that naturally hedges the net monetary loss.
- **CONSENSUS and VALUATION were `[PLACEHOLDER]`** until Stage 2's live run confirmed the
  market-perception hypothesis on 2026-09-27 — see "Market perception — confirmed" above;
  both fields in `config.py` now reflect that finding, not a placeholder.
