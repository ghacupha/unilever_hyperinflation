"""Load and validate a REIT config.py file. Mirrors the load/validate pattern used
elsewhere in bizplan, adapted to the REIT config's actual fields."""
import importlib.util
import os

REQUIRED_FIELDS = [
    "BUSINESS_NAME", "OUTPUT_PREFIX", "CURRENCY", "YEARS", "TAX_RATE",
    "PROPERTIES", "RENTAL_INCOME", "OPEX_ITEMS", "CAPITAL", "UNITS",
    "REGULATORY", "MACRO_SCENARIOS", "VALUATION", "PEER_REITS",
    "ACTUALS", "ACTUAL_YEARS", "CURRENCY_UNIT_ABBR", "REGULATOR_NAME",
]


def load_config(path):
    """Load config.py using importlib. Returns the module object."""
    abs_path = os.path.abspath(path)
    if not os.path.isfile(abs_path):
        raise FileNotFoundError(f"config.py not found at: {abs_path}")
    spec = importlib.util.spec_from_file_location("reit_config", abs_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate_reit_config(config):
    """Validate required fields and basic shape. Returns list of errors."""
    errors = []

    for field in REQUIRED_FIELDS:
        if not hasattr(config, field):
            errors.append(f"Missing required field: {field}")

    if hasattr(config, "YEARS") and len(config.YEARS) < 1:
        errors.append("YEARS must have at least one entry")

    if hasattr(config, "PROPERTIES"):
        for i, prop in enumerate(config.PROPERTIES):
            for key in ("name", "location", "beds", "opening_fair_value", "tier"):
                if key not in prop:
                    errors.append(f"PROPERTIES[{i}] missing '{key}'")
            if "tier" in prop and prop["tier"] not in ("seed", "stabilized"):
                errors.append(f"PROPERTIES[{i}]['tier'] must be 'seed' or 'stabilized', "
                               f"got {prop['tier']!r}")

    if hasattr(config, "REGULATORY"):
        for key in ("payout_min", "ltv_max", "income_producing_min"):
            if key not in config.REGULATORY:
                errors.append(f"REGULATORY missing '{key}'")

    if hasattr(config, "MACRO_SCENARIOS"):
        w = config.MACRO_SCENARIOS.get("weights", {})
        if w and abs(sum(w.values()) - 1.0) > 1e-9:
            errors.append(f"MACRO_SCENARIOS weights must sum to 1.0, got {sum(w.values())}")

    return errors


def load_and_validate(path):
    """Load config and raise ValueError if validation fails."""
    config = load_config(path)
    errors = validate_reit_config(config)
    if errors:
        raise ValueError("config.py validation failed:\n" + "\n".join(f"  - {e}" for e in errors))
    return config
