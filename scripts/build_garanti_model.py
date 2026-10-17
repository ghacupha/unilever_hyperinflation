#!/usr/bin/env python3
# Copyright (c) 2026 Edwin Njeru. Licensed under the MIT License (see LICENSE).

"""Entry point: build the Garanti BBVA net-monetary-position workbook (BLUEPRINT.md
Phase 5). Not routed through `bizplan.config_loader` -- that module's `REQUIRED_FIELDS`
schema is specific to the Unilever-style fictional-subsidiary model; Garanti's config is
a real disclosed balance sheet with a structurally different shape.

Usage:
    .venv/bin/python scripts/build_garanti_model.py
    .venv/bin/python scripts/build_garanti_model.py --config path/to/config.py
"""
import argparse
import importlib.util
import os
import sys

_ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT_DIR)

from bizplan.financial import bank_excel_renderer


def load_config(path):
    spec = importlib.util.spec_from_file_location("garanti_config", path)
    config = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config)
    return config


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default=None,
                         help="Path to config.py (default: examples/garanti_bbva/config.py)")
    args = parser.parse_args()

    config_path = args.config or os.path.join(_ROOT_DIR, "examples", "garanti_bbva", "config.py")
    config = load_config(config_path)

    output_dir = os.environ.get("OUTPUT_DIR", os.path.dirname(config_path))
    os.makedirs(output_dir, exist_ok=True)
    output_path = bank_excel_renderer.save_workbook(config, output_dir)
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
