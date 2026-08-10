#!/usr/bin/env python3
"""Entry point: build a REIT financial model workbook.

Usage:
    .venv/bin/python scripts/build_reit_model.py
    .venv/bin/python scripts/build_reit_model.py --reit acorn_i_reit
    .venv/bin/python scripts/build_reit_model.py --config path/to/config.py
"""
import argparse
import os
import sys

_ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT_DIR)

from bizplan.config_loader import load_and_validate
from bizplan.financial import reit_calculations
from bizplan.financial import reit_excel_renderer


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reit", default="acorn_i_reit",
                         help="REIT example folder name under examples/ (default: acorn_i_reit)")
    parser.add_argument("--config", default=None,
                         help="Explicit path to a config.py — overrides --reit")
    args = parser.parse_args()

    config_path = args.config or os.path.join(_ROOT_DIR, "examples", args.reit, "config.py")
    config = load_and_validate(config_path)

    results = reit_calculations.build_all(config)

    output_dir = os.environ.get("OUTPUT_DIR", os.path.dirname(config_path))
    output_path = os.path.join(output_dir, f"{config.OUTPUT_PREFIX}_Financial_Model.xlsx")
    reit_excel_renderer.build_excel(config, results, output_path)
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
