# AGENTS.md

Index of agent-related resources in this repo.

## Bank/financial-institution onboarding

- **SOP**: [`.devops/agents/bank-onboarding.md`](.devops/agents/bank-onboarding.md) —
  the institution-agnostic playbook (data intake, extraction, known pitfalls,
  `config.py` schema, verification, seasonal updates).
- **Runnable agent**: [`agent/`](agent/) — a standalone Python program that
  executes the SOP: researches a new institution's public filings (Anthropic
  API, server-side web search + native PDF reading), writes
  `examples/<institution>/config.py` and `research_output.md`, runs the
  existing renderer, and can be re-run later (`update`) to ingest new
  annual/quarterly filings and roll the model forward. See `agent/cli.py`
  for usage. Requires `ANTHROPIC_API_KEY`; each run costs real API tokens.

## Equity Research Report pipeline (preliminary — see BLUEPRINT.md "2026-07-26 (cont.)")

- **SOP**: [`.devops/agents/equity-report/model-sourcing.md`](.devops/agents/equity-report/model-sourcing.md) —
  generalizes `bank-onboarding.md` along a second axis: institution *and* an
  as-of anchor year (actuals = the 3 years ending there, projections = the
  next 5 forward). Supports rolling forward (seasonal updates) and rolling
  backward (backtesting a past vantage point).
- **Runnable stage**: [`scripts/source_model.py`](scripts/source_model.py) —
  unlike `agent/`, this runs via `claude -p` (Claude Code's own headless
  mode), authenticated through a Claude subscription rather than a raw
  `ANTHROPIC_API_KEY` — no separate per-token billing. Requires the `claude`
  CLI on `PATH`, logged in normally (never pass `--bare`, which forces
  API-key billing). Usage: `python scripts/source_model.py <institution>
  --as-of <year> [hint-url ...]`.
- Validation after sourcing is deterministic Python, not a re-prompt:
  `bizplan/financial/bank_validation.py` re-implements the Model sheet's
  Master Check (Balance Sheet / Capital Adequacy / Liquidity) so a broken
  model is caught before anything downstream (later report-writing stages)
  runs. `bizplan/financial/report_data.py` serializes the valuation/
  scenario/sensitivity output those later stages will read.
