# Copyright (c) 2026 Edwin Njeru. Licensed under the MIT License (see LICENSE).

import pytest

from bizplan.config_loader import load_and_validate, load_config, validate_config

VALID_CONFIG = '''
BUSINESS_NAME = "Test Co"
OUTPUT_PREFIX = "Test"
CURRENCY = "EUR"
YEARS = [2024, 2025]
ACTUAL_YEARS = [2024, 2025]
SUBSIDIARIES = {{
    "testland": dict(local_currency="TST", hyperinflationary_since="2020-01-01",
                      monetary_items=["cash"], non_monetary_items=["ppe"]),
}}
INFLATION_INDICES = {{"testland": {{2024: dict(index_open=100.0, index_close=110.0)}}}}
FX_RATES = {{"testland": {{2024: dict(fx_open=1.0, fx_close=1.0)}}}}
ACCOUNTING_SCENARIOS = {{"current_rate": {{}}, "us_gaap_temporal": {{}}, "ias29_ias21": {{}}}}
ACTUALS = {{}}
VALIDATION_ACTUALS = {{}}
CONSENSUS = {{}}
VALUATION = {{}}
{extra}
'''


def _write_config(tmp_path, extra=""):
    path = tmp_path / "config.py"
    path.write_text(VALID_CONFIG.format(extra=extra))
    return str(path)


def test_load_and_validate_real_unilever_config_passes(unilever_config):
    assert unilever_config.BUSINESS_NAME.startswith("Unilever")


def test_valid_minimal_config_passes(tmp_path):
    config = load_and_validate(_write_config(tmp_path))
    assert config.CURRENCY == "EUR"


def test_load_config_missing_file_raises():
    with pytest.raises(FileNotFoundError):
        load_config("/no/such/path/config.py")


def test_missing_required_field_is_reported(tmp_path):
    path = tmp_path / "config.py"
    path.write_text("BUSINESS_NAME = 'x'\n")
    config = load_config(str(path))
    errors = validate_config(config)
    assert any("OUTPUT_PREFIX" in e for e in errors)
    assert any("SUBSIDIARIES" in e for e in errors)


def test_years_empty_is_reported(tmp_path):
    config = load_config(_write_config(tmp_path, extra="YEARS = []"))
    errors = validate_config(config)
    assert any("YEARS" in e for e in errors)


def test_subsidiary_missing_key_is_reported(tmp_path):
    extra = (
        'SUBSIDIARIES = {"testland": dict(local_currency="TST")}'
    )
    config = load_config(_write_config(tmp_path, extra=extra))
    errors = validate_config(config)
    assert any("hyperinflationary_since" in e for e in errors)
    assert any("monetary_items" in e for e in errors)
    assert any("non_monetary_items" in e for e in errors)


def test_accounting_scenarios_wrong_keys_is_reported(tmp_path):
    extra = 'ACCOUNTING_SCENARIOS = {"current_rate": {}}'
    config = load_config(_write_config(tmp_path, extra=extra))
    errors = validate_config(config)
    assert any("ACCOUNTING_SCENARIOS" in e for e in errors)


def test_inflation_indices_empty_series_is_reported(tmp_path):
    extra = 'INFLATION_INDICES = {"testland": {}}'
    config = load_config(_write_config(tmp_path, extra=extra))
    errors = validate_config(config)
    assert any("INFLATION_INDICES" in e for e in errors)


def test_load_and_validate_raises_on_invalid_config(tmp_path):
    path = tmp_path / "config.py"
    path.write_text("BUSINESS_NAME = 'x'\n")
    with pytest.raises(ValueError):
        load_and_validate(str(path))
