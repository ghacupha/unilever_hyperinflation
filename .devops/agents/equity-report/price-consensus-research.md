# Price / consensus research SOP

Stage 2 of the equity-report pipeline. Given an institution (with a ticker/exchange) and
a **reference date**, research two things and write them as structured JSON — nothing
else. This stage does no valuation math and drafts no report prose; later stages read
your JSON output as ground truth for the market side of the comparison (the model side
comes from Stage 1's `valuation_inputs.json`).

## 1. The reference date is not "today" — read it carefully

You will be given an explicit reference date. If it equals today's date, research current
live data as normal. **If it's in the past, this is a backtest** — research the
institution exactly as it stood *as of that date*, using only filings, prices, and news
dated on or before it. Do not use hindsight: no later share price, no later analyst
report, no later news, even if it would be more accurate. A backtest that leaks later
information isn't testing anything real. If you cannot find data contemporaneous with the
reference date, say so explicitly in your output rather than substituting more recent data
silently.

## 2. Share price

Find the closing share price on (or the nearest trading day before) the reference date,
from a named, citable source (exchange site, a financial data aggregator, etc.) — not a
vague "around X". Record the source and the exact date the price is for.

## 3. Analyst consensus — and specifically, does it price in the hyperinflation effect?

Search for sell-side analyst coverage: consensus target price, consensus rating
(Buy/Hold/Sell or equivalent), number of analysts covering the stock. For this
institution's report, the specific question that matters most is: **does real analyst
commentary distinguish the IAS 29 net monetary gain/(loss) from ordinary FX translation,
or does it get folded into a generic "FX headwind" and effectively ignored as a one-off
non-cash item?** Search sell-side notes, earnings-call transcripts, and analyst
commentary specifically for how they discuss the hyperinflationary subsidiaries — quote
what you find. Do not fabricate a consensus or pad it with unrelated sources. If no
analyst consensus is findable:
- Say so explicitly (`consensus_found: false`).
- Propose one documented, clearly-labeled proxy instead — e.g. how the institution's own
  investor-relations materials or earnings-call Q&A frame the hyperinflationary
  subsidiaries' contribution. Label it as a proxy, not a real consensus, and say why you
  chose it.
  **If the proxy needs any figure the model itself computes (net monetary gain/loss,
  the IAS 29 impact table, monetary-exposure grades), read it from
  `valuation_inputs.json`'s `company_facts` / `ias29_impact_primary_year` /
  `monetary_exposure` blocks — you'll be given its path. Do not independently research or
  derive that figure from a filing or web source.** That JSON is the model's own
  corrected ground truth; a live web search can turn up a different (e.g. superseded or
  note-vs-primary-statement) figure that looks equally plausible but is inconsistent with
  the rest of this report.

## 4. Output format

Write **only** a JSON object (no prose commentary outside it) with this shape:

```json
{
  "institution": "...",
  "reference_date": "YYYY-MM-DD",
  "is_backtest": true/false,
  "share_price": {
    "value": 0.0,
    "currency": "...",
    "as_of_date": "YYYY-MM-DD",
    "source": "..."
  },
  "consensus_found": true/false,
  "consensus": {
    "target_price": 0.0,
    "rating": "Buy/Hold/Sell/...",
    "num_analysts": 0,
    "source": "..."
  },
  "proxy_used": {
    "description": "...",
    "implied_value": 0.0,
    "rationale": "..."
  },
  "notes": "Anything a later report-writing stage needs to know about data quality, gaps, or caveats."
}
```

Omit `consensus` if `consensus_found` is `false`; omit `proxy_used` if a real consensus
was found. Write this JSON to the exact file path you're given in the task instruction —
use your file-editing tools directly, the same way Stage 0's model-sourcing SOP does.
