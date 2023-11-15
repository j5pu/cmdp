from pathlib import Path

import pytest
from typer.testing import Result

from nodeps.__main__ import *
from nodeps import NODEPS_PROJECT_NAME


@pytest.mark.parametrize("clirun", [[_branch]], indirect=True)
def test_branch(clirun: Result):
    assert clirun.exit_code == 0
    assert clirun.stdout == "main\n"


@pytest.mark.parametrize("clirun", [[_build]], indirect=True)
def test_build(clirun: Result):
    assert clirun.exit_code == 0


@pytest.mark.parametrize("clirun", [[_build, str(Path(__file__))]], indirect=True)
def test_build_path(clirun: Result):
    assert clirun.exit_code == 0


@pytest.mark.parametrize("clirun", [[_build, NODEPS_PROJECT_NAME]], indirect=True)
def test_build_name(clirun: Result):
    assert clirun.exit_code == 0


@pytest.mark.parametrize("clirun", [[_builds]], indirect=True)
def test_builds(clirun: Result):
    assert clirun.exit_code == 0


@pytest.mark.parametrize("clirun", [[_buildrequires]], indirect=True)
def test_buildrequires(clirun: Result):
    assert clirun.exit_code == 0


@pytest.mark.parametrize("clirun", [[_current]], indirect=True)
def test_current(clirun: Result):
    assert clirun.exit_code == 0
    assert clirun.stdout == "main\n"


@pytest.mark.parametrize("clirun", [[_dependencies]], indirect=True)
def test_dependencies(clirun: Result):
    assert clirun.exit_code == 0


@pytest.mark.parametrize("clirun", [[_distribution]], indirect=True)
def test_distribution(clirun: Result):
    assert clirun.exit_code == 0


@pytest.mark.parametrize("clirun", [[_extras]], indirect=True)
def test_extras(clirun: Result):
    assert clirun.exit_code == 0


@pytest.mark.parametrize("clirun", [[_ipythondir]], indirect=True)
def test_ipythondir(clirun: Result):
    assert clirun.exit_code == 0
    assert "ipython" in clirun.stdout


@pytest.mark.parametrize("clirun", [[_latest]], indirect=True)
def test_latest(clirun: Result):
    assert clirun.exit_code == 0


@pytest.mark.parametrize("clirun", [[_mip]], indirect=True)
def test_mip(clirun: Result):
    assert clirun.exit_code == 0
    assert "." in clirun.stdout


@pytest.mark.parametrize("clirun", [[_next]], indirect=True)
def test_next(clirun: Result):
    assert clirun.exit_code == 0


@pytest.mark.parametrize("clirun", [[_pythonstartup]], indirect=True)
def test_pythonstartup(clirun: Result):
    assert clirun.exit_code == 0
    assert "python_startup" in clirun.stdout


@pytest.mark.parametrize("clirun", [[_remote]], indirect=True)
def test_remote(clirun: Result):
    assert clirun.exit_code == 0
    assert "https://" in clirun.stdout


@pytest.mark.parametrize("clirun", [[_repos]], indirect=True)
def test_repos(clirun: Result):
    assert clirun.exit_code == 0


@pytest.mark.parametrize("clirun", [[_superproject]], indirect=True)
def test_superproject(clirun: Result):
    assert clirun.exit_code == 0


@pytest.mark.parametrize("clirun", [[_version]], indirect=True)
def test_version(clirun: Result):
    assert clirun.exit_code == 0


@pytest.mark.parametrize("clirun", [[_venv]], indirect=True)
def test_venv(clirun: Result):
    assert clirun.exit_code == 0
