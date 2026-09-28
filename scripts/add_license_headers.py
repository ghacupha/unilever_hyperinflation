#!/usr/bin/env python3
# Copyright (c) 2026 Edwin Njeru. Licensed under the MIT License (see LICENSE).

"""Adds an MIT license header to every first-party .py source file that doesn't already
have one. Idempotent -- safe to re-run any time new files are added.

Scope: bizplan/, scripts/, tests/, and examples/unilever/config.py (the repo's own
authored source). Deliberately excludes timestamped sample-run directories under
examples/ (e.g. examples/2026-09-27_222102/) -- those are frozen output snapshots, not
source code, the same reason they're never hand-edited elsewhere in this repo.

Usage:
    .venv/bin/python scripts/add_license_headers.py
"""
import os

_ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

HEADER = "# Copyright (c) 2026 Edwin Njeru. Licensed under the MIT License (see LICENSE).\n"
MARKER = "Licensed under the MIT License"

TARGET_DIRS = ["bizplan", "scripts", "tests"]
EXTRA_FILES = [os.path.join("examples", "unilever", "config.py")]


def _iter_target_files():
    for target_dir in TARGET_DIRS:
        for dirpath, _dirnames, filenames in os.walk(os.path.join(_ROOT_DIR, target_dir)):
            for name in filenames:
                if name.endswith(".py"):
                    yield os.path.join(dirpath, name)
    for rel_path in EXTRA_FILES:
        yield os.path.join(_ROOT_DIR, rel_path)


def add_header(path):
    with open(path, encoding="utf-8") as f:
        content = f.read()

    if MARKER in content:
        return False

    lines = content.splitlines(keepends=True)
    insert_at = 1 if lines and lines[0].startswith("#!") else 0
    lines[insert_at:insert_at] = [HEADER, "\n"]
    with open(path, "w", encoding="utf-8") as f:
        f.writelines(lines)
    return True


def main():
    updated, skipped = [], []
    for path in sorted(set(_iter_target_files())):
        if not os.path.isfile(path):
            continue
        rel = os.path.relpath(path, _ROOT_DIR)
        if add_header(path):
            updated.append(rel)
        else:
            skipped.append(rel)

    for rel in updated:
        print(f"added header: {rel}")
    print(f"\n{len(updated)} file(s) updated, {len(skipped)} already had a header.")


if __name__ == "__main__":
    main()
