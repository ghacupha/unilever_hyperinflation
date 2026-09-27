import os
import sys

import pytest
from pytest_bdd import given

_ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT_DIR)

from bizplan.config_loader import load_and_validate  # noqa: E402

UNILEVER_CONFIG_PATH = os.path.join(_ROOT_DIR, "examples", "unilever", "config.py")


@pytest.fixture
def unilever_config():
    """A fresh load of the real, calibrated Unilever config for every test — config.py
    modules are plain namespaces, so tests that mutate one (e.g. to break calibration on
    purpose) can't leak state into other tests."""
    return load_and_validate(UNILEVER_CONFIG_PATH)


# Shared BDD steps -- available to every feature file's step module below, since
# conftest.py fixtures/steps are visible repo-wide within tests/. Published under the
# name "config" (not "unilever_config") to avoid colliding with the plain @pytest.fixture
# above, which plain (non-BDD) tests request directly.

@given("the calibrated Unilever configuration", target_fixture="config")
def _given_calibrated_config():
    return load_and_validate(UNILEVER_CONFIG_PATH)


@given("a copy of the calibrated Unilever configuration", target_fixture="config")
def _given_a_copy_of_calibrated_config():
    """Same as above under different Gherkin wording -- a fresh load either way, so
    'a copy' is exactly as safe to mutate as the original (see unilever_config fixture)."""
    return load_and_validate(UNILEVER_CONFIG_PATH)
