from pathlib import Path

import pytest

from nodeps.__main__ import *
from nodeps import NODEPS_PROJECT_NAME


@pytest.mark.parametrize("invoke", [[_build]], indirect=True)
def test_build(invoke):
    assert invoke.exit_code == 0


@pytest.mark.parametrize("invoke", [[_build, str(Path(__file__))]], indirect=True)
def test_build_path(invoke):
    assert invoke.exit_code == 0


@pytest.mark.parametrize("invoke", [[_build, NODEPS_PROJECT_NAME]], indirect=True)
def test_build_name(invoke):
    assert invoke.exit_code == 0


@pytest.mark.parametrize("invoke", [[_buildrequires]], indirect=True)
def test_buildrequires(invoke):
    assert invoke.exit_code == 0


@pytest.mark.parametrize("invoke", [[_commit]], indirect=True)
def test_commit(invoke):
    assert invoke.exit_code == 0


@pytest.mark.parametrize("invoke", [[_dependencies]], indirect=True)
def test_dependencies(invoke):
    assert invoke.exit_code == 0


@pytest.mark.parametrize("invoke", [[_distribution]], indirect=True)
def test_distribution(invoke):
    assert invoke.exit_code == 0


@pytest.mark.parametrize("invoke", [[_extras]], indirect=True)
def test_extras(invoke):
    assert invoke.exit_code == 0


@pytest.mark.parametrize("invoke", [[_latest]], indirect=True)
def test_latest(invoke):
    assert invoke.exit_code == 0


@pytest.mark.parametrize("invoke", [[_next]], indirect=True)
def test_next(invoke):
    assert invoke.exit_code == 0


@pytest.mark.parametrize("invoke", [[_repos]], indirect=True)
def test_repos(invoke):
    assert invoke.exit_code == 0


@pytest.mark.parametrize("invoke", [[_sha]], indirect=True)
def test_sha(invoke):
    assert invoke.exit_code == 0


@pytest.mark.parametrize("invoke", [[_superproject]], indirect=True)
def test_superproject(invoke):
    assert invoke.exit_code == 0


@pytest.mark.parametrize("invoke", [[_version]], indirect=True)
def test_version(invoke):
    assert invoke.exit_code == 0


@pytest.mark.parametrize("invoke", [[_venv]], indirect=True)
def test_venv(invoke):
    assert invoke.exit_code == 0
