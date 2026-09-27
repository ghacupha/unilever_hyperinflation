from bizplan.report import data as report_data


def _worlds_with_ratio(ratio, total_assets=1000.0):
    monetary_gain_loss = ratio * total_assets
    return dict(C=dict(monetary_gain_loss=monetary_gain_loss, total_assets=total_assets))


def test_monetary_exposure_grade_bands():
    cases = [(0.04, "A"), (0.10, "B"), (0.25, "C"), (0.40, "D"), (0.60, "F"),
             (-0.10, "B")]  # sign shouldn't matter, only magnitude
    for ratio, expected_grade in cases:
        grades = report_data.monetary_exposure_grades({"sub": _worlds_with_ratio(ratio)})
        assert grades["sub"]["grade"] == expected_grade, f"ratio {ratio} -> {grades['sub']['grade']}"


def test_overall_grade_is_worst_of_subsidiaries():
    grades = report_data.monetary_exposure_grades({
        "good": _worlds_with_ratio(0.02),
        "bad": _worlds_with_ratio(0.45),
    })
    assert grades["good"]["grade"] == "A"
    assert grades["bad"]["grade"] == "D"
    assert grades["overall_grade"] == "D"


def test_company_facts_uses_primary_calibrated_year(unilever_config):
    facts = report_data.company_facts(unilever_config)
    assert facts["as_of_year"] == min(unilever_config.YEARS)
    assert set(unilever_config.SUBSIDIARIES) == set(facts["subsidiaries"])


def test_to_report_json_has_expected_top_level_keys(unilever_config):
    computed = report_data.compute(unilever_config)
    report_json = report_data.to_report_json(unilever_config, computed)
    for key in ("business_name", "currency", "company_facts",
                "ias29_impact_primary_year", "scenario_comparison",
                "validation_gap", "monetary_exposure", "consensus", "valuation"):
        assert key in report_json


def test_write_report_data_writes_valid_json(tmp_path, unilever_config):
    import json
    computed = report_data.compute(unilever_config)
    path, data = report_data.write_report_data(unilever_config, computed, str(tmp_path))
    with open(path) as f:
        on_disk = json.load(f)
    assert on_disk["business_name"] == data["business_name"]
