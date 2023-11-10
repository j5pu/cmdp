"""Pytest fixtures."""
__all__ = (
    "Repos",
    "repos",
)

import dataclasses
import logging
import shutil
from collections.abc import Generator

import pytest

from ..extras import Repo
from ..modules.constants import DOCKER_COMMAND
from ..modules.path import Path

LOGGER = logging.getLogger(__name__)


def _config(*args):
    for arg in args:
        arg.config_writer().set_value("user", "name", "root").release()
        arg.config_writer().set_value("user", "email", "root@example.com").release()
        arg.config_writer().set_value("pull", "rebase", "false").release()


@dataclasses.dataclass
class Repos:
    """Local and remote fixture class.

    Attributes:
        clone: A clone of the remote repository
        local: A local repository pushed to remote repository
        remote: A remote repository
    """
    clone: Repo
    local: Repo
    remote: Repo


def pytest_collection_modifyitems(config, items):
    """Mark skip_docker if --local or not DOCKER_COMMAND.

    Examples:
        >>> @pytest.mark.skip
        >>> def test_skip_docker(local: bool):
        ...     assert local is False
    """
    # TODO: https://docs.pytest.org/en/7.1.x/example/markers.html#custom-marker-and-command-line-option-to-control-test-runs
    skip_docker = pytest.mark.skip(reason="Only run when --local or not DOCKER_COMMAND")
    for item in items:
        if config.getoption("local") is True or not DOCKER_COMMAND:
            item.add_marker(skip_docker)
        # skip_docker = pytest.mark.skip(reason="Only run when --local or not DOCKER_COMMAND")
        # for item in items:
        #     if "skip_docker" in item.keywords:
        #         item.add_marker(skip_docker)


@pytest.hookimpl
def pytest_addoption(parser):
    """Use config local to skip tests.

    Example:
        >>> @pytest.mark.skipif("config.getoption('local') is True", reason='--local option provided')
        >>> def test_func_docker(local: bool):
        ...     assert local is False
    """
    parser.addoption('--local', action='store_true', dest="local", default=False, help='Run local tests.')

@pytest.fixture()
def local(request) -> bool:
    """Fixture to see if --local option passed to pytest.

    Examples:
        pytest --local tests/test_fixture.py::test_fixture_local
    """
    return request.config.getoption('local')


@pytest.fixture()
def repos(tmp_path: Path) -> Generator[Repos]:
    """Provides an instance of :class:`nodeps._repo.Repo` for a local and a remote repository."""
    tmp = tmp_path / "repos"
    local = Repo.init(tmp / "local", initial_branch="main")
    remote = Repo.init(tmp / "remote.git", bare=True)
    _config(local, remote)
    local.create_remote('origin', remote.git_dir)
    origin = local.remote(name='origin')
    top = Path(local.top)
    top.touch("README.md")
    local.git.add(".")
    local.git.commit("-a", "-m", "First commit.")
    local.git.push("--set-upstream", "origin", "main")
    origin.push()
    clone = remote.clone(tmp / "clone", branch="main")
    _config(clone)

    LOGGER.debug(f"clone: {clone.top}")  # noqa: G004
    LOGGER.debug(f"local: {top}")  # noqa: G004
    LOGGER.debug(f"remote: {remote.top}")  # noqa: G004

    yield Repos(clone=clone, local=local, remote=remote)

    shutil.rmtree(tmp, ignore_errors=True)
