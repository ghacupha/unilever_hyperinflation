"""Runs the existing, institution-agnostic renderer pipeline unchanged.

The agent's job stops at producing examples/<institution>/config.py — the
actual calculation/rendering engine (bizplan/financial/{bank_calculations,
bank_excel_renderer}.py) is never touched here."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def run_build(institution: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "build_bank_model.py"), "--bank", institution],
        cwd=REPO_ROOT, capture_output=True, text=True,
    )
