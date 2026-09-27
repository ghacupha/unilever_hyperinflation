import os
import sys

import pytest

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
