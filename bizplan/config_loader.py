# Copyright (c) 2026 Edwin Njeru. Licensed under the MIT License (see LICENSE).

"""Load and validate a hyperinflation-model config.py file. Mirrors the load/validate
pattern used elsewhere in bizplan, adapted to this domain's actual fields."""
import importlib.util
import os

REQUIRED_FIELDS = [
    "BUSINESS_NAME", "OUTPUT_PREFIX", "CURRENCY", "YEARS", "ACTUAL_YEARS",
    "SUBSIDIARIES", "INFLATION_INDICES", "FX_RATES", "ACCOUNTING_SCENARIOS",
    "ACTUALS", "VALIDATION_ACTUALS", "CONSENSUS", "VALUATION",
]


def load_config(path):
    """Load config.py using importlib. Returns the module object."""
    abs_path = os.path.abspath(path)
    if not os.path.isfile(abs_path):
        raise FileNotFoundError(f"config.py not found at: {abs_path}")
    spec = importlib.util.spec_from_file_location("hyperinflation_config", abs_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate_config(config):
    """Validate required fields and basic shape. Returns list of errors."""
    errors = []

    for field in REQUIRED_FIELDS:
        if not hasattr(config, field):
            errors.append(f"Missing required field: {field}")

    if hasattr(config, "YEARS") and len(config.YEARS) < 1:
        errors.append("YEARS must have at least one entry")

    if hasattr(config, "SUBSIDIARIES"):
        for name, sub in config.SUBSIDIARIES.items():
            for key in ("local_currency", "hyperinflationary_since", "monetary_items",
                        "non_monetary_items"):
                if key not in sub:
                    errors.append(f"SUBSIDIARIES[{name!r}] missing '{key}'")

    if hasattr(config, "ACCOUNTING_SCENARIOS"):
        expected = {"current_rate", "us_gaap_temporal", "ias29_ias21"}
        got = set(config.ACCOUNTING_SCENARIOS.keys())
        if got != expected:
            errors.append(f"ACCOUNTING_SCENARIOS must have keys {expected}, got {got}")

    if hasattr(config, "INFLATION_INDICES"):
        for name, series in config.INFLATION_INDICES.items():
            if not series:
                errors.append(f"INFLATION_INDICES[{name!r}] is empty")

    return errors


def load_and_validate(path):
    """Load config and raise ValueError if validation fails."""
    config = load_config(path)
    errors = validate_config(config)
    if errors:
        raise ValueError("config.py validation failed:\n" + "\n".join(f"  - {e}" for e in errors))
    return config
