# Copyright (c) 2026 Edwin Njeru. Licensed under the MIT License (see LICENSE).

from pytest_bdd import given, parsers, scenarios, then, when

from bizplan.financial import hyperinflation_calculations as calc
from bizplan.report import data as report_data, validation as report_validation

scenarios("features/calibration.feature")


@given(parsers.parse('Unilever\'s real disclosed 2024 IAS 29 impact figures for "{subsidiary}"'),
       target_fixture="subsidiary")
def _given_disclosed_figures(subsidiary):
    return subsidiary


@when("the hyperinflation model is built from the calibrated Unilever configuration",
      target_fixture="model_results")
def _when_model_built(unilever_config):
    return calc.build_model(unilever_config)


@then(parsers.parse('the model\'s {metric} impact for "{subsidiary}" matches the disclosed '
                     'figure within 0.01 EURm'))
def _then_impact_matches_disclosed(unilever_config, model_results, subsidiary, metric):
    year = min(unilever_config.YEARS)
    modeled = model_results[year]["subsidiaries"][subsidiary]["impact"][metric]
    disclosed = unilever_config.DISCLOSED_IMPACT_2024[subsidiary][metric]
    assert abs(modeled - disclosed) <= 0.01, f"{subsidiary}.{metric}: {modeled} vs {disclosed}"


@when("Argentina's disclosed revenue input is doubled by mistake",
      target_fixture="validation_result")
def _when_revenue_doubled(config):
    primary_year = min(config.YEARS)
    config.ACTUALS["argentina"][primary_year]["rev"] *= 2.0
    computed = report_data.compute(config)
    return report_validation.validate_model(config, computed)


@then("the calibration-fidelity validator reports the model as not ok")
def _then_not_ok(validation_result):
    assert validation_result["ok"] is False


@then("it flags Argentina's turnover figure as outside tolerance")
def _then_turnover_flagged(validation_result):
    gap = validation_result["primary_year"]["calibration"]["argentina"]["turnover"]
    assert gap["within_tolerance"] is False
