#!/usr/bin/env python3
"""Entry point: build a bank financial model workbook.

Usage:
    .venv/bin/python scripts/build_bank_model.py
    .venv/bin/python scripts/build_bank_model.py --bank family_bank_kenya
    .venv/bin/python scripts/build_bank_model.py --config path/to/config.py
"""
import argparse
import os
import sys

_ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT_DIR)

from bizplan.config_loader import load_and_validate
from bizplan.financial import bank_calculations
from bizplan.financial import bank_excel_renderer


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bank", default="family_bank_kenya",
                         help="Bank example folder name under examples/ (default: family_bank_kenya)")
    parser.add_argument("--config", default=None,
                         help="Explicit path to a config.py — overrides --bank")
    args = parser.parse_args()

    config_path = args.config or os.path.join(_ROOT_DIR, "examples", args.bank, "config.py")
    config = load_and_validate(config_path)

    results = bank_calculations.build_all(config)

    output_dir = os.environ.get("OUTPUT_DIR", os.path.dirname(config_path))
    output_path = os.path.join(output_dir, f"{config.OUTPUT_PREFIX}_Financial_Model.xlsx")
    bank_excel_renderer.build_excel(config, results, output_path)
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
