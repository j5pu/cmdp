import sysconfig
from pathlib import Path


import nodeps
from nodeps.fixtures import skip_docker

from pip._internal.cli.main import main as _main

ROOT = Path(__file__).parent.parent
PACKAGE = nodeps.__name__


def setup_module():
    """ setup any state specific to the execution of the given module."""
    rc = _main(["install", "-q", str(ROOT)])
    assert rc == 0


def teardown_module():
    """teardown any state that was previously setup with a setup_module method."""
    if not nodeps.in_tox():
        _main(["uninstall", "-q", "-y", PACKAGE])


@skip_docker
def test_install() -> None:
    """Test that the package is installed."""
    paths = sysconfig.get_paths()
    purelib = Path(paths["purelib"])
    scripts = Path(paths["scripts"])
    assert (purelib / f"{PACKAGE}.pth").is_file()
    assert (scripts / f"git-mod-add").is_file()
    assert (purelib / f"{PACKAGE}/data/Brewfile").is_file()
