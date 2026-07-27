"""Load and validate a bank config.py file. Mirrors the load/validate pattern used in
colossal-visuals/bizplan/config_loader.py, adapted to the bank config's actual fields."""
import importlib.util
import os

REQUIRED_FIELDS = [
    "BUSINESS_NAME", "OUTPUT_PREFIX", "CURRENCY", "YEARS", "TAX_RATE",
    "LOAN_SEGMENTS", "DEPOSIT_TYPES", "INVESTMENT_SECURITIES", "OPEX_ITEMS",
    "CAPITAL", "MACRO_SCENARIOS", "VALUATION", "PEER_BANKS",
    "ACTUALS", "ACTUAL_YEARS", "REGULATORY_CAPITAL",
    "CURRENCY_UNIT_ABBR", "REGULATOR_NAME", "BS_SPLIT_RATIOS",
]


def load_config(path):
    """Load config.py using importlib. Returns the module object."""
    abs_path = os.path.abspath(path)
    if not os.path.isfile(abs_path):
        raise FileNotFoundError(f"config.py not found at: {abs_path}")
    spec = importlib.util.spec_from_file_location("bank_config", abs_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate_bank_config(config):
    """Validate required fields and basic shape. Returns list of errors."""
    errors = []

    for field in REQUIRED_FIELDS:
        if not hasattr(config, field):
            errors.append(f"Missing required field: {field}")

    if hasattr(config, "YEARS") and len(config.YEARS) < 1:
        errors.append("YEARS must have at least one entry")

    if hasattr(config, "LOAN_SEGMENTS"):
        for i, seg in enumerate(config.LOAN_SEGMENTS):
            for key in ("opening_s1", "opening_s2", "opening_s3", "loss_rate_s1",
                        "loss_rate_s2", "loss_rate_s3", "growth", "yield_rate", "risk_weight"):
                if key not in seg:
                    errors.append(f"LOAN_SEGMENTS[{i}] missing '{key}'")

    if hasattr(config, "MACRO_SCENARIOS"):
        w = config.MACRO_SCENARIOS.get("weights", {})
        if w and abs(sum(w.values()) - 1.0) > 1e-9:
            errors.append(f"MACRO_SCENARIOS weights must sum to 1.0, got {sum(w.values())}")

    return errors


def load_and_validate(path):
    """Load config and raise ValueError if validation fails."""
    config = load_config(path)
    errors = validate_bank_config(config)
    if errors:
        raise ValueError("config.py validation failed:\n" + "\n".join(f"  - {e}" for e in errors))
    return config
