"""Per-institution manifest: tracks what's already been ingested so seasonal
updates only look for genuinely new filings rather than re-downloading
everything each run."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


def manifest_path(institution_dir: Path) -> Path:
    return institution_dir / "manifest.json"


def load(institution_dir: Path) -> dict:
    path = manifest_path(institution_dir)
    if not path.exists():
        return {"institution": institution_dir.name, "sources": []}
    return json.loads(path.read_text(encoding="utf-8"))


def save(institution_dir: Path, data: dict) -> None:
    manifest_path(institution_dir).write_text(json.dumps(data, indent=2), encoding="utf-8")


def content_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def record_source(data: dict, url: str, local_path: Path, period: str) -> None:
    data["sources"].append({
        "url": url,
        "local_path": str(local_path),
        "sha256": content_hash(local_path) if local_path.exists() else None,
        "period": period,
    })
