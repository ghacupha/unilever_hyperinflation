# Copyright (c) 2026 Edwin Njeru. Licensed under the MIT License (see LICENSE).

"""Shared helper for invoking `claude -p` (Claude Code's headless/print mode) as a
pipeline stage. Every equity-report stage that needs an LLM call (sourcing, price
research, section drafting, review) goes through this one function instead of each
hand-rolling the same subprocess plumbing.

Deliberately never passes `--bare` — that flag forces raw-`ANTHROPIC_API_KEY` billing.
Run without it, `claude -p` authenticates the same way an interactive session does
(subscription OAuth) and draws from the same per-seat allowance, not separate per-token
billing. See BLUEPRINT.md's "Equity Research Report pipeline" section.
"""
import subprocess
import sys


def run_stage(sop_path, task_prompt, cwd, permission_mode="bypassPermissions"):
    """Reads `sop_path` as the system prompt, runs `claude -p` with `task_prompt`, and
    returns stdout. Raises `RuntimeError` on a non-zero exit."""
    system_prompt = sop_path.read_text(encoding="utf-8")
    cmd = [
        "claude", "-p",
        "--append-system-prompt", system_prompt,
        "--permission-mode", permission_mode,
        task_prompt,
    ]
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        raise RuntimeError(f"claude -p failed (exit {result.returncode})")
    return result.stdout
