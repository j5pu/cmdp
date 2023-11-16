"""pytest fixture tests."""

import logging
import sys

import pytest
from click.testing import Result

from nodeps import DOCKER
from nodeps.__main__ import project_p
from nodeps.fixtures import Cli, Repos, repos, skip_docker

LOGGER = logging.getLogger(__name__)


@pytest.mark.parametrize("cli", [[project_p]], indirect=True)
def test_cli(cli: Cli):
    assert cli.result.exit_code == 0
    assert "Show this message and exit" in cli.result.stdout


@pytest.mark.parametrize("clirun", [[project_p]], indirect=True)
def test_clirun(clirun: Result):
    assert clirun.exit_code == 0
    assert "Show this message and exit" in clirun.stdout


def test_fixture_repos(repos: Repos):
    """Test that repos are created and pushed."""
    assert (repos.local.top / "README.md").is_file()
    assert repos.local.git.cat_file("-e", "origin/main:README.md") == ""
    assert (repos.clone.top / "README.md").is_file()


def test_fixture_local(local: bool):
    """Test that --local option fixture has value."""
    if DOCKER or "--local" in sys.argv:
        assert local is True
    else:
        assert local is False
    assert isinstance(local, bool)


@skip_docker
def test_skip_docker(local: bool):
    """pytest --local tests/test_fixture.py::test_skip_docker."""
    assert local is False


@pytest.mark.skipif("config.getoption('local') is True", reason='--local option provided')
def test_func_skipif_local_docker(local: bool):
    """Should run if local is False or not --local in command."""
    assert local is False
