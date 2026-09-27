from pytest_bdd import scenarios, then, when

from bizplan.report import data as report_data, recommendation

scenarios("features/report_data_generation.feature")


@when("the ground-truth report data is generated", target_fixture="report_json")
def _when_report_data_generated(config):
    computed = report_data.compute(config)
    return report_data.to_report_json(config, computed)


@then("the report JSON's scenario comparison has entries for World A, World B, and World C")
def _then_scenario_comparison_has_all_worlds(report_json):
    comparison = report_json["scenario_comparison"]
    for row in comparison.values():
        assert set(row.keys()) == {"A", "B", "C"}


@then("the report JSON's monetary exposure has a grade for every subsidiary")
def _then_monetary_exposure_has_every_subsidiary(config, report_json):
    exposure = report_json["monetary_exposure"]
    for name in config.SUBSIDIARIES:
        assert "grade" in exposure[name]


@then("it has an overall grade")
def _then_has_overall_grade(report_json):
    assert "overall_grade" in report_json["monetary_exposure"]


@when("the mechanical recommendation is computed from that report data",
      target_fixture="decision")
def _when_recommendation_from_report_data(report_json):
    return recommendation.mechanical_recommendation(report_json)


@then("the recommendation's net monetary figure matches the report JSON's company facts")
def _then_net_monetary_matches(decision, report_json):
    assert decision["net_monetary_gain_loss"] == report_json["company_facts"]["net_monetary_gain_loss_eur"]


@then("the recommendation's operating profit figure matches the report JSON's company facts")
def _then_operating_profit_matches(decision, report_json):
    assert decision["operating_profit"] == report_json["company_facts"]["operating_profit_eur"]
