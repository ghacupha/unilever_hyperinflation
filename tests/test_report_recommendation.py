# Copyright (c) 2026 Edwin Njeru. Licensed under the MIT License (see LICENSE).

from bizplan.report import data as report_data, recommendation


def _report_json(net_monetary, op_profit, exposure=None):
    return dict(
        company_facts=dict(net_monetary_gain_loss_eur=net_monetary, operating_profit_eur=op_profit),
        monetary_exposure=exposure or {
            "argentina": dict(grade="C"), "turkiye": dict(grade="A"), "overall_grade": "C",
        },
    )


def test_immaterial_signal_below_threshold():
    decision = recommendation.mechanical_recommendation(_report_json(-100.0, 10000.0))
    assert decision["material"] is False
    assert decision["mechanical_signal"] == "Flag: immaterial"


def test_material_signal_above_threshold():
    decision = recommendation.mechanical_recommendation(_report_json(-150.0, 1000.0))
    assert decision["material"] is True
    assert decision["mechanical_signal"] == "Flag: material"


def test_ratio_is_absolute_value_based():
    decision = recommendation.mechanical_recommendation(_report_json(150.0, 1000.0))
    assert decision["ratio"] == 0.15
    assert decision["material"] is True


def test_worst_exposure_subsidiary_picks_lowest_grade():
    exposure = {"argentina": dict(grade="B"), "turkiye": dict(grade="F"), "overall_grade": "F"}
    decision = recommendation.mechanical_recommendation(_report_json(-10.0, 1000.0, exposure))
    assert decision["worst_exposure_subsidiary"] == "turkiye"


def test_real_unilever_config_comes_back_immaterial(unilever_config):
    """Regression check against the real calibrated model: Unilever's group-level net
    monetary loss is small relative to its (illustrative-scale) group operating profit,
    so the signal should read immaterial -- this was a genuine finding, not a bug, when
    the live pipeline first ran (see CHANGELOG.md)."""
    computed = report_data.compute(unilever_config)
    report_json = report_data.to_report_json(unilever_config, computed)
    decision = recommendation.mechanical_recommendation(report_json)
    assert decision["mechanical_signal"] == "Flag: immaterial"


def test_write_recommendation_writes_json(tmp_path):
    import json
    path, decision = recommendation.write_recommendation(_report_json(-50.0, 1000.0), str(tmp_path))
    with open(path) as f:
        on_disk = json.load(f)
    assert on_disk["mechanical_signal"] == decision["mechanical_signal"]
