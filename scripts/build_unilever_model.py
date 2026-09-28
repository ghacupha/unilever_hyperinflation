#!/usr/bin/env python3
# Copyright (c) 2026 Edwin Njeru. Licensed under the MIT License (see LICENSE).

"""Entry point: build the Unilever hyperinflation-accounting model workbook.

Usage:
    .venv/bin/python scripts/build_unilever_model.py
    .venv/bin/python scripts/build_unilever_model.py --instance unilever
    .venv/bin/python scripts/build_unilever_model.py --config path/to/config.py
"""
import argparse
import os
import sys

_ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT_DIR)

from bizplan.config_loader import load_and_validate
from bizplan.financial import hyperinflation_calculations
from bizplan.financial import hyperinflation_excel_renderer


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", default="unilever",
                         help="Example folder name under examples/ (default: unilever)")
    parser.add_argument("--config", default=None,
                         help="Explicit path to a config.py — overrides --instance")
    args = parser.parse_args()

    config_path = args.config or os.path.join(_ROOT_DIR, "examples", args.instance, "config.py")
    config = load_and_validate(config_path)

    results = hyperinflation_calculations.build_model(config)

    output_dir = os.environ.get("OUTPUT_DIR", os.path.dirname(config_path))
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{config.OUTPUT_PREFIX}_Financial_Model.xlsx")
    hyperinflation_excel_renderer.build_excel(config, results, output_path)
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
