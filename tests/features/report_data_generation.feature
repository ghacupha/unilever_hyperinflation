Feature: Deterministic report data generation
  Before any `claude -p`-driven drafting happens, the pipeline's deterministic stages
  (ground truth, validation, the mechanical recommendation) must produce internally
  consistent output -- every later report section reads these JSON files as its only
  source of numbers, so if they disagree with each other or with the model, every
  section built on top of them would be wrong too. This feature deliberately stays
  within the pure-Python stages -- no live `claude -p` calls, so it runs fast and
  deterministically in CI.

  Scenario: The generated report JSON carries a scenario comparison for every world
    Given the calibrated Unilever configuration
    When the ground-truth report data is generated
    Then the report JSON's scenario comparison has entries for World A, World B, and World C

  Scenario: The generated report JSON carries a monetary-exposure grade per subsidiary
    Given the calibrated Unilever configuration
    When the ground-truth report data is generated
    Then the report JSON's monetary exposure has a grade for every subsidiary
    And it has an overall grade

  Scenario: The mechanical recommendation is consistent with the report JSON it reads
    Given the calibrated Unilever configuration
    When the ground-truth report data is generated
    And the mechanical recommendation is computed from that report data
    Then the recommendation's net monetary figure matches the report JSON's company facts
    And the recommendation's operating profit figure matches the report JSON's company facts
