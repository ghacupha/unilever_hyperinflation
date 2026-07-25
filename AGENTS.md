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
