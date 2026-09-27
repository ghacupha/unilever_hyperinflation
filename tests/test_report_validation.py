from bizplan.financial import hyperinflation_calculations as calc
from bizplan.report import data as report_data, validation as report_validation


def test_validate_model_passes_for_real_config(unilever_config):
    computed = report_data.compute(unilever_config)
    result = report_validation.validate_model(unilever_config, computed)
    assert result["ok"] is True
    for name in unilever_config.SUBSIDIARIES:
        for gap in result["primary_year"]["calibration"][name].values():
            assert gap["within_tolerance"] is True


def test_validate_model_fails_when_calibration_is_broken(unilever_config):
    """Mutate the calibrated inputs (the fixture is a fresh load per test, so this
    can't leak into other tests) so the model no longer reproduces the real disclosed
    2024 figures -- validate_model() must catch it, not silently pass."""
    primary_year = min(unilever_config.YEARS)
    unilever_config.ACTUALS["argentina"][primary_year]["rev"] *= 2.0

    computed = calc.build_model(unilever_config)
    result = report_validation.validate_model(unilever_config, computed)

    assert result["ok"] is False
    argentina_gaps = result["primary_year"]["calibration"]["argentina"]
    assert argentina_gaps["turnover"]["within_tolerance"] is False


def test_write_validation_result_writes_json(tmp_path, unilever_config):
    import json
    computed = report_data.compute(unilever_config)
    path, result = report_validation.write_validation_result(unilever_config, computed, str(tmp_path))
    with open(path) as f:
        on_disk = json.load(f)
    assert on_disk["ok"] == result["ok"]
