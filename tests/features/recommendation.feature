Feature: Mechanical earnings-quality recommendation signal
  Stage 3 of the equity-report pipeline flags whether the net monetary gain/(loss) is
  material relative to group operating profit -- a documented 10% threshold. This is
  pure arithmetic, no LLM involved, and it's the mechanical half of the report's
  eventual Buy/Hold/Sell-style call.

  Scenario: A small monetary effect relative to group operating profit is immaterial
    Given a group with a net monetary loss of 100.0 and operating profit of 10000.0
    When the mechanical recommendation is computed
    Then the signal is "Flag: immaterial"
    And the recommendation is not material

  Scenario: A large monetary effect relative to group operating profit is material
    Given a group with a net monetary loss of 150.0 and operating profit of 1000.0
    When the mechanical recommendation is computed
    Then the signal is "Flag: material"
    And the recommendation is material

  Scenario: The real calibrated Unilever model comes back immaterial
    Given the calibrated Unilever configuration
    When the full deterministic pipeline computes the report data and recommendation
    Then the signal is "Flag: immaterial"
