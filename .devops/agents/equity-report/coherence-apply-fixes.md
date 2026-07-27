# Section SOP: Coherence Gate — Apply Fixes

Stage 5.5 of the equity-report pipeline (the "optimizer" half of an evaluator-optimizer
loop; Stage 5's review is the "evaluator" half). You are given a list of specific,
already-diagnosed findings from Stage 5's review — your job is narrow: fix exactly those
issues, in the exact files named, and nothing else.

## 1. Scope — fix only what's named

Each finding names a `section` (a report section file under `<output_dir>/sections/`) and
describes a specific problem: a factual claim that contradicts the model's own ground
truth, a near-verbatim passage, or a cross-section contradiction. Edit only the named
section file(s), and only the specific sentence/passage the finding describes. Do not
rewrite, restructure, or "improve" anything else in the file — this is a surgical
correction pass, not a redraft.

## 2. Ground truth hierarchy

When a finding says a section's stated value doesn't match `valuation_inputs.json`'s
`company_facts` block (or another JSON ground-truth file), **the JSON is right and the
section text is wrong** — the Excel financial model (and the JSON files derived from it)
always take precedence over report prose or `research_output.md`. Never adjust a number
to split the difference or to preserve the section's original phrasing; use the exact
correct value and re-word the surrounding sentence only as much as needed to state it
correctly.

## 3. No new research

Do not use any web-search or network tool. Every fix in scope for this stage is a
report-text-vs-already-fetched-ground-truth mismatch — the correct value already exists
in one of the JSON files you're given paths to. If a finding genuinely can't be resolved
from those files alone (it describes a gap in the *data*, not the *text*), leave that
finding's issue unresolved rather than researching new information to fill it — say so
plainly if asked, but do not silently invent or re-derive a number.

## 4. What not to touch

Never modify `valuation_inputs.json`, `price_consensus_research.json`,
`recommendation_decision.json`, `research_output.md`, `config.py`, or the Excel model
file. Those are the ground truth this stage's fixes conform *to* — correcting the model
to match the report, instead of the reverse, would silently break the model's own
internal consistency (the Balance Sheet Check, the live formula chain) for the sake of
matching a narrative error.

## 5. Output

Edit the named section file(s) directly with your Edit tool. Do not write any new files
and do not report back in prose — the next pipeline stage re-runs Stage 5's review
against your edits to confirm the findings are actually resolved, so there's no summary
to write here.
