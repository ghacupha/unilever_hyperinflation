Feature: Hyperinflation model calibration
  The Unilever hyperinflation model builds a small, fully hand-traceable fictional
  subsidiary for Argentina and for Turkiye, algebraically solved so that running it
  through the World A/B/C engine reproduces Unilever's own real disclosed 2024 IAS 29
  impact figures. This is the model's core promise -- if it stops holding, the model
  is no longer calibrated to reality.

  Scenario Outline: The model reproduces Unilever's real disclosed 2024 IAS 29 impact
    Given Unilever's real disclosed 2024 IAS 29 impact figures for "<subsidiary>"
    When the hyperinflation model is built from the calibrated Unilever configuration
    Then the model's <metric> impact for "<subsidiary>" matches the disclosed figure within 0.01 EURm

    Examples: Argentina
      | subsidiary | metric                  |
      | argentina  | total_assets            |
      | argentina  | turnover                |
      | argentina  | operating_profit        |
      | argentina  | net_monetary_gain_loss  |

    Examples: Turkiye
      | subsidiary | metric                  |
      | turkiye    | total_assets            |
      | turkiye    | turnover                |
      | turkiye    | operating_profit        |
      | turkiye    | net_monetary_gain_loss  |

  Scenario: A broken calibration is caught, not silently accepted
    Given a copy of the calibrated Unilever configuration
    When Argentina's disclosed revenue input is doubled by mistake
    Then the calibration-fidelity validator reports the model as not ok
    And it flags Argentina's turnover figure as outside tolerance
