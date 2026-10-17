# Copyright (c) 2026 Edwin Njeru. Licensed under the MIT License (see LICENSE).

import pytest

from bizplan.financial import bank_monetary_position as bmp


@pytest.fixture
def garanti_config():
    import importlib.util
    import os
    path = os.path.join(os.path.dirname(__file__), "..", "examples", "garanti_bbva", "config.py")
    spec = importlib.util.spec_from_file_location("garanti_config", path)
    config = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config)
    return config


def test_monetary_totals_split_sums_to_balance_sheet_total(garanti_config):
    """Every line item is flagged monetary or non-monetary -- the two buckets must sum
    back to the real published Total Assets / Total Liabilities for both years, or the
    classification has silently dropped or double-counted a line."""
    bs = garanti_config.BALANCE_SHEET
    for year in (2024, 2025):
        assets = bmp.monetary_totals(bs, year, "assets")
        liabilities = bmp.monetary_totals(bs, year, "liabilities")
        assert assets["monetary"] + assets["non_monetary"] == sum(
            v[str(year)] for v in bs["assets"].values()
        )
        assert liabilities["monetary"] + liabilities["non_monetary"] == sum(
            v[str(year)] for v in bs["liabilities"].values()
        )


def test_net_monetary_position_is_a_net_asset_both_years(garanti_config):
    """Garanti's loan book dwarfs its deposit base enough that it sits as a net monetary
    *asset* in both years -- a useful contrast with Unilever's Argentina, which the
    existing model finds to be a net monetary *liability* that still books a loss."""
    bs = garanti_config.BALANCE_SHEET
    assert bmp.net_monetary_position(bs, 2024) > 0
    assert bmp.net_monetary_position(bs, 2025) > 0


def test_recover_original_purchasing_power_identity(garanti_config):
    """Recovering a value to the same year it's already shown in is a no-op."""
    cpi = garanti_config.CPI_INDEX
    value = 1_000_000
    assert bmp.recover_original_purchasing_power(value, 2025, 2025, cpi) == value


def test_recover_original_purchasing_power_matches_hand_derivation(garanti_config):
    cpi = garanti_config.CPI_INDEX
    recovered = bmp.recover_original_purchasing_power(1348.17, shown_in_year=2025,
                                                        original_year=2024, cpi_index=cpi)
    assert recovered == pytest.approx(1029.82, rel=1e-9)


def test_estimate_monetary_result_returns_none_without_prior_cpi(garanti_config):
    """2024's own estimate needs a Dec-2023 closing balance sheet (to recover the Dec-2023
    opening position) -- this model only has the FY2024/FY2025 balance sheet columns, so
    FY2024 has no estimate, only FY2025 does."""
    assert bmp.estimate_monetary_result(garanti_config, 2024) is None
    assert bmp.estimate_monetary_result(garanti_config, 2025) is not None


def test_fy2025_estimate_is_a_loss_consistent_with_net_asset_position(garanti_config):
    """A net monetary *asset* position during inflation should produce an estimated
    *loss*, matching the sign (though not the size) of Garanti's own disclosed figure."""
    estimate = bmp.estimate_monetary_result(garanti_config, 2025)
    assert estimate < 0
    assert garanti_config.DISCLOSED_NET_MONETARY_RESULT["2025"] < 0


def test_compare_to_disclosed_reports_a_large_documented_gap(garanti_config):
    """The naive opening-NMP x inflation estimate overstates Garanti's real monetary
    loss by roughly an order of magnitude -- a genuine finding (a bank's monetary
    position is actively managed intrayear, unlike a static year-end snapshot), not a
    bug to tune away. This test pins the gap's existence and rough scale so a future
    change to the classification/estimate logic can't silently make this close to zero
    without someone noticing and re-checking the finding still holds."""
    comparison = bmp.compare_to_disclosed(garanti_config, 2025)
    assert comparison["gap_multiple"] > 5  # order-of-magnitude overstatement, not noise


def test_build_model_covers_every_configured_year(garanti_config):
    model = bmp.build_model(garanti_config)
    assert set(model["years"].keys()) == set(garanti_config.YEARS)
    assert model["years"][2024]["comparison"] is None
    assert model["years"][2025]["comparison"] is not None
