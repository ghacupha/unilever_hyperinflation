# Copyright (c) 2026 Edwin Njeru. Licensed under the MIT License (see LICENSE).

from pytest_bdd import given, parsers, scenarios, then, when

from bizplan.report import data as report_data, recommendation

scenarios("features/recommendation.feature")


@given(parsers.parse("a group with a net monetary loss of {loss:g} and operating profit of {profit:g}"),
       target_fixture="report_json")
def _given_group_figures(loss, profit):
    return dict(
        company_facts=dict(net_monetary_gain_loss_eur=-loss, operating_profit_eur=profit),
        monetary_exposure={"only": dict(grade="C"), "overall_grade": "C"},
    )


@when("the mechanical recommendation is computed", target_fixture="decision")
def _when_recommendation_computed(report_json):
    return recommendation.mechanical_recommendation(report_json)


@then(parsers.parse('the signal is "{expected_signal}"'))
def _then_signal_is(decision, expected_signal):
    assert decision["mechanical_signal"] == expected_signal


@then("the recommendation is material")
def _then_is_material(decision):
    assert decision["material"] is True


@then("the recommendation is not material")
def _then_is_not_material(decision):
    assert decision["material"] is False


@when("the full deterministic pipeline computes the report data and recommendation",
      target_fixture="decision")
def _when_full_pipeline(config):
    computed = report_data.compute(config)
    report_json = report_data.to_report_json(config, computed)
    return recommendation.mechanical_recommendation(report_json)
