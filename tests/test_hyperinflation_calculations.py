# Copyright (c) 2026 Edwin Njeru. Licensed under the MIT License (see LICENSE).

import pytest

from bizplan.financial import hyperinflation_calculations as calc

FLAT_LOCAL = dict(
    rev=1000.0, cogs=500.0, opex=200.0, dep=50.0, capex=60.0,
    nonmon_assets_open=800.0, mon_assets_close=400.0, mon_liab_close=300.0,
    equity_open=900.0,
)


def test_no_inflation_no_fx_movement_worlds_agree():
    """With a flat index and flat FX, restatement/remeasurement should be a no-op --
    every line-item World A, B, and C produce must be identical. Their two plugs (World
    B's remeasurement gain/loss, World C's monetary gain/loss) reduce to the same
    nominal-arithmetic residual and must therefore agree with each other too -- but that
    residual isn't necessarily zero for an arbitrary (not cash-flow-consistent) fixture
    like FLAT_LOCAL, where capex/the monetary-position change aren't tied to a financing
    source. World A's is always exactly 0.0 by definition -- it never computes a plug at
    all -- which is a design fact about the code, not an emergent property of flatness."""
    worlds = calc.restate_and_translate(FLAT_LOCAL, idx_open=100.0, idx_close=100.0,
                                         fx_open=10.0, fx_close=10.0)
    A, B, C = worlds["A"], worlds["B"], worlds["C"]
    for key in ("revenue", "cogs", "opex", "depreciation", "operating_profit",
                "total_assets", "non_monetary_assets", "equity"):
        assert A[key] == B[key] == C[key]
    assert A["monetary_gain_loss"] == 0.0
    assert B["monetary_gain_loss"] == C["monetary_gain_loss"]


def test_no_inflation_no_fx_movement_zero_plug_for_a_self_consistent_fixture():
    """Given a fixture where the monetary-position change during the year is exactly
    the operating profit generated (i.e. profit is held entirely as cash, the simplest
    self-consistent roll-forward), the World B/C plug genuinely is zero under flat
    macro conditions -- confirming the -24 residual above is about FLAT_LOCAL's
    financing assumptions, not a bug."""
    rev, cogs, opex, dep, capex = 1000.0, 500.0, 200.0, 50.0, 0.0
    nonmon_assets_open, mon_liab_close, equity_open = 800.0, 300.0, 900.0
    op_profit = rev - cogs - opex - dep  # 250.0
    # Solved so (nonmon_open + capex - dep + mon_assets_close) - mon_liab_close
    # - equity_open - op_profit == 0 -- the balance-sheet identity the plug enforces.
    mon_assets_close = mon_liab_close + equity_open + op_profit - nonmon_assets_open - capex + dep
    consistent = dict(
        rev=rev, cogs=cogs, opex=opex, dep=dep, capex=capex,
        nonmon_assets_open=nonmon_assets_open, mon_assets_close=mon_assets_close,
        mon_liab_close=mon_liab_close, equity_open=equity_open,
    )
    worlds = calc.restate_and_translate(consistent, idx_open=100.0, idx_close=100.0,
                                         fx_open=10.0, fx_close=10.0)
    assert worlds["B"]["monetary_gain_loss"] == pytest.approx(0.0, abs=1e-9)
    assert worlds["C"]["monetary_gain_loss"] == pytest.approx(0.0, abs=1e-9)


def test_inflation_only_raises_restated_nonmonetary_assets():
    """Pure inflation restatement (no FX movement) can only ever raise non-monetary
    assets in local terms -- this is the structural reason total-assets impact can't
    flip sign in this model (see research_output.md)."""
    worlds = calc.restate_and_translate(FLAT_LOCAL, idx_open=100.0, idx_close=200.0,
                                         fx_open=10.0, fx_close=10.0)
    assert worlds["C"]["non_monetary_assets"] > worlds["A"]["non_monetary_assets"]
    assert worlds["C"]["total_assets"] > worlds["A"]["total_assets"]


def test_monetary_gain_loss_is_the_exact_balancing_plug():
    """IAS 29's net monetary gain/(loss) must be exactly the figure that makes the
    restated balance sheet tie out: restated assets - liabilities - opening equity -
    operating profit. This is not an approximation -- verify it holds to float
    precision for a case with real inflation and real FX movement."""
    idx_open, idx_close, fx_open, fx_close = 100.0, 218.0, 850.0, 1010.0
    worlds = calc.restate_and_translate(FLAT_LOCAL, idx_open, idx_close, fx_open, fx_close)
    C = worlds["C"]
    implied_equity = C["total_assets"] - (FLAT_LOCAL["mon_liab_close"] / fx_close)
    residual = implied_equity - C["equity"]
    assert abs(residual) < 1e-9


def test_impact_vs_current_rate_is_world_c_minus_world_a():
    worlds = calc.restate_and_translate(FLAT_LOCAL, idx_open=100.0, idx_close=150.0,
                                         fx_open=20.0, fx_close=24.0)
    impact = calc.impact_vs_current_rate(worlds)
    assert impact["total_assets"] == worlds["C"]["total_assets"] - worlds["A"]["total_assets"]
    assert impact["turnover"] == worlds["C"]["revenue"] - worlds["A"]["revenue"]
    assert impact["operating_profit"] == (worlds["C"]["operating_profit"]
                                           - worlds["A"]["operating_profit"])
    assert impact["net_monetary_gain_loss"] == worlds["C"]["monetary_gain_loss"]


def test_consolidate_sums_subsidiaries_and_other_ops():
    sub_a = calc.restate_and_translate(FLAT_LOCAL, 100.0, 150.0, 20.0, 24.0)
    sub_b = calc.restate_and_translate(FLAT_LOCAL, 100.0, 130.0, 5.0, 6.0)
    other = dict(revenue=10.0, cogs=4.0, operating_profit=3.0, total_assets=50.0,
                 equity=30.0, non_monetary_assets=40.0, monetary_gain_loss=0.0)
    consolidated = calc.consolidate({"a": sub_a, "b": sub_b}, other)
    for world in ("A", "B", "C"):
        expected = (sub_a[world]["revenue"] + sub_b[world]["revenue"] + other["revenue"])
        assert consolidated[world]["revenue"] == expected


def test_ratios_formulas():
    world = dict(revenue=200.0, total_assets=1000.0, equity=600.0, operating_profit=50.0)
    r = calc.ratios(world)
    assert r["roa"] == 50.0 / 1000.0
    assert r["asset_turnover"] == 200.0 / 1000.0
    assert r["debt_to_equity"] == (1000.0 - 600.0) / 600.0


def test_ratios_handles_zero_total_assets():
    r = calc.ratios(dict(revenue=1.0, total_assets=0.0, equity=0.0, operating_profit=1.0))
    assert r["roa"] == 0.0
    assert r["asset_turnover"] == 0.0
    assert r["debt_to_equity"] == 0.0


def test_scenario_comparison_table_has_all_worlds_for_every_row():
    worlds = calc.restate_and_translate(FLAT_LOCAL, 100.0, 140.0, 30.0, 33.0)
    other = dict(revenue=0.0, cogs=0.0, operating_profit=0.0, total_assets=0.0,
                 equity=0.0, non_monetary_assets=0.0, monetary_gain_loss=0.0)
    consolidated = calc.consolidate({"only": worlds}, other)
    table = calc.scenario_comparison_table(consolidated)
    for row in ("revenue", "cogs", "operating_profit", "non_monetary_assets",
                "total_assets", "equity", "monetary_gain_loss", "roa",
                "asset_turnover", "debt_to_equity"):
        assert set(table[row].keys()) == {"A", "B", "C"}


def test_validate_against_disclosed_same_sign_and_gap():
    model = dict(total_assets=10.0, turnover=-5.0, operating_profit=0.0, net_monetary_gain_loss=3.0)
    disclosed = dict(total_assets=12.0, turnover=5.0, operating_profit=0.0, net_monetary_gain_loss=-1.0)
    gap = calc.validate_against_disclosed(model, disclosed)
    assert gap["total_assets"]["abs_gap"] == 10.0 - 12.0
    assert gap["total_assets"]["same_sign"] is True
    assert gap["turnover"]["same_sign"] is False
    assert gap["operating_profit"]["pct_gap"] is None  # disclosed == 0
    assert gap["net_monetary_gain_loss"]["same_sign"] is False


def test_restated_closing_local_equity_matches_translated_equity():
    """The local (untranslated) restated closing equity from restated_closing_local()
    should equal World C's translated equity times the closing FX rate -- two different
    code paths computing the same underlying figure must agree."""
    idx_open, idx_close, fx_open, fx_close = 100.0, 175.0, 40.0, 45.0
    closing = calc.restated_closing_local(FLAT_LOCAL, idx_open, idx_close, fx_open, fx_close)
    worlds = calc.restate_and_translate(FLAT_LOCAL, idx_open, idx_close, fx_open, fx_close)
    assert abs(closing["equity_close"] - worlds["C"]["equity"] * fx_close) < 1e-6


def test_build_model_reproduces_real_disclosed_2024_figures(unilever_config):
    """The whole point of the 2024 calibration: running the real config through the
    engine must reproduce Unilever's own disclosed 2024 IAS 29 impact table to within a
    tight tolerance. If this ever fails, the calibration in config.py is broken."""
    results = calc.build_model(unilever_config)
    year = min(unilever_config.YEARS)
    for name, disclosed in unilever_config.DISCLOSED_IMPACT_2024.items():
        impact = results[year]["subsidiaries"][name]["impact"]
        for key, expected in disclosed.items():
            assert impact[key] == pytest.approx(expected, abs=0.01), (
                f"{name}.{key}: expected {expected}, got {impact[key]}"
            )


def test_build_model_validation_present_for_every_year(unilever_config):
    results = calc.build_model(unilever_config)
    for year in unilever_config.YEARS:
        assert results[year]["validation"] is not None
        for name in unilever_config.SUBSIDIARIES:
            assert name in results[year]["validation"]

