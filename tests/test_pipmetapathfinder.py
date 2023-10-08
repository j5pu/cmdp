import sys
import sysconfig
from pathlib import Path

import pytest

import nodeps

from pip._internal.cli.main import main as _main

ROOT = Path(__file__).parent.parent
PACKAGE = "sampleproject"


def teardown_module():
    """teardown any state that was previously setup with a setup_module method."""
    if not nodeps.in_tox():
        _main(["uninstall", "-q", "-y", PACKAGE])


@pytest.mark.skipif(nodeps.in_tox(), reason="in tox")
def test_pipmetapathfinder() -> None:
    with pytest.raises(ModuleNotFoundError):
        import sampleproject  # type: ignore[attr-defined]
    with nodeps.pipmetapathfinder():  # doctest: +SKIP
        print(sys.meta_path)
        import sampleproject  # type: ignore[attr-defined]
        assert sampleproject.__name__ == PACKAGE
        assert PACKAGE in sys.modules
