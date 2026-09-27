# CLAUDE.md

# General behavioral guidelines

Behavioral guidelines to reduce common LLM coding mistakes. Merge with project-specific instructions as needed.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

---

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.

## Agent Instructions

- Keep `.memories/session/plan.md` as the current plan source and update root
  `plan.md` for easy reference when adding features.
- Update `CHANGELOG.md` for meaningful code changes.
- Put new agent behavior files under `.devops/agents/` and reference them from
  `AGENTS.md` and `CLAUDE.md`.
- Do not revert user changes in a dirty worktree.
- Prefer the repo's existing patterns over new abstractions.
- Use `rg` for search.
- Use `apply_patch` for manual edits.
- Avoid destructive git or filesystem operations unless explicitly requested.

## Unilever Hyperinflation-Accounting Model — progress tracking

This repo's active initiative is a CFA Level II Financial Statement Analysis teaching
model — the *Multinational Operations* / hyperinflation-accounting (IAS 29) reading,
illustrated with Unilever plc's real disclosed treatment of its Argentina and Türkiye
subsidiaries. Three root-level files track it — **read them before starting work, update
them before stopping**:

- `BLUEPRINT.md` — the design source of truth (the real-world case, the calculation
  engine's World A/B/C mechanics, the Excel renderer's structure, known simplifications).
  Update it when a design decision changes.
- `BACKLOG.md` — phase-by-phase task checklist; read it first to know what's next.
- `CHANGELOG.md` — append an entry for every meaningful chunk of work, naming which
  blueprint phase / backlog item(s) it closes.

Primary data source for calibration is `examples/unilever/research_output.md` (Unilever's
own SEC-filed Form 20-F hyperinflation accounting policy notes for 2024 and 2025) — the
model's subsidiary-level local-currency inputs are a fictional-but-reconciling
illustration solved algebraically to reproduce those real disclosed aggregate figures;
see `research_output.md`'s "Calibration method" for the full derivation before treating
any subsidiary-level figure as a real disclosure.

The prior REIT-model design lives in git history — `bizplan/financial/reit_calculations.py`
and `reit_excel_renderer.py` were retired when the repo pivoted to this domain
(2026-09-27). `bizplan/report/*` (the equity-research-report pipeline) was adapted the
same day (`BACKLOG.md` Phase 3) — its deterministic stages are verified end-to-end; the
`claude -p`-driven stages haven't yet had a live run.

See `AGENTS.md` for the equity-research-report pipeline (SOPs under
`.devops/agents/equity-report/`).