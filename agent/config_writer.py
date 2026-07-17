"""Turns the agent's extracted facts into examples/<institution>/config.py,
validated immediately against bizplan/config_loader's schema — fail fast on a
malformed config rather than letting a bad field surface as a deep KeyError
inside the renderer."""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from bizplan.config_loader import load_and_validate  # noqa: E402


def write_config(institution_dir: Path, config_source: str) -> None:
    """`config_source` is a complete Python module body (the agent's output).
    Written to disk, then loaded and validated against REQUIRED_FIELDS —
    raises ValueError on schema violations so the caller can feed the error
    back to the extraction step and retry rather than silently shipping a
    broken config."""
    config_path = institution_dir / "config.py"
    config_path.write_text(config_source, encoding="utf-8")
    load_and_validate(str(config_path))
