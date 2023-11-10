"""pytest fixture tests."""

import logging
import sys

import pytest

from nodeps import DOCKER_COMMAND
from nodeps.fixtures import Repos, repos

LOGGER = logging.getLogger(__name__)


def test_fixture_repos(repos: Repos):
    """Test that repos are created and pushed."""
    assert (repos.local.top / "README.md").is_file()
    assert repos.local.git.cat_file("-e", "origin/main:README.md") == ""
    assert (repos.clone.top / "README.md").is_file()


def test_fixture_local(local: bool):
    """Test that --local option fixture has value."""
    print(local, file=sys.stderr)
    assert isinstance(local, bool)


@pytest.mark.skipif()
def test_skip_docker(local: bool):
    assert local is False or not DOCKER_COMMAND


@pytest.mark.skipif("config.getoption('local') is True", reason='--local option provided')
def test_func_skipif_local_docker(local: bool):
    """Should run if local is False or not --local in command."""
    assert local is False
