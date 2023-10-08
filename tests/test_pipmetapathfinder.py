import sys
from pathlib import Path

import pytest

import nodeps

from pip._internal.cli.main import main as _main

ROOT = Path(__file__).parent.parent
PACKAGE = "simplejson"


def setup_module():
    """teardown any state that was previously setup with a setup_module method."""
    if not nodeps.in_tox():
        _main(["uninstall", "-q", "-y", PACKAGE])


def teardown_module():
    """teardown any state that was previously setup with a setup_module method."""
    if not nodeps.in_tox():
        _main(["uninstall", "-q", "-y", PACKAGE])


@pytest.mark.skipif(nodeps.in_tox(), reason="in tox")
def test_pipmetapathfinder() -> None:
    with nodeps.pipmetapathfinder():  # doctest: +SKIP
        import simplejson  # type: ignore[attr-defined]
        assert simplejson.__name__ == PACKAGE
        assert PACKAGE in sys.modules
