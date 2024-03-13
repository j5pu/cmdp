"""Pytest fixtures.

Pytest functions execution order:
    pytest_addoption
    pytest_configure
    pytest_sessionstart
    pytest_generate_tests
    pytest_collection_modifyitems
"""
from __future__ import annotations

__all__ = (
    "Cli",
    "Repos",
    "cli",
    "clirun",
    "local",
    "logger",
    "pytest_addoption",
    "pytest_collection_modifyitems",
    "pytest_configure",
    "pytest_generate_tests",
    "pytest_sessionstart",
    "repos",
    "rootpath",
    "skip_docker",
)

import contextlib
import dataclasses
import logging
import shutil
from typing import TYPE_CHECKING

import pytest
from typer.testing import CliRunner, Result

from nodeps.extras import Repo
from nodeps.modules.constants import CI, DOCKER
from nodeps.modules.functions import in_tox
from nodeps.modules.gh import git_config_global
from nodeps.modules.path import Path

if TYPE_CHECKING:
    from collections.abc import Generator
    from types import TracebackType

    from _pytest import nodes
    from _pytest.config import Config
    from _pytest.config.argparsing import Parser
    from _pytest.fixtures import FixtureRequest, SubRequest
    from _pytest.main import Session
    from _pytest.python import Metafunc

LOGGER = logging.getLogger(__name__)
runner: CliRunner = CliRunner(mix_stderr=False)


@dataclasses.dataclass
class Cli:
    """Helper class for CLI runner test fixture."""
    exit_code: int
    exc_info: tuple[type[BaseException], BaseException, TracebackType] | None
    exception: BaseException | None
    rc: int
    """exit_code."""
    result: Result
    """result instance."""
    runner: CliRunner
    stderr: str
    stderr_bytes: bytes
    stdout: str
    stdout_bytes: bytes


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


@pytest.fixture()
def cli(request: SubRequest) -> Cli:
    r"""CLI runner invoke fixture.

    Examples:
        >>> @pytest.mark.parametrize("cli", [["command", "--option"]], indirect=True)
        ... def test_current(cli: Cli):
        ...    assert cli.result.exit_code == 0
        ...    assert cli.result.stdout == "main"
    """
    result = runner.invoke(request.param[0], request.param[1:], catch_exceptions=False)
    return Cli(
        exit_code=result.exit_code,
        exc_info=result.exc_info,
        exception=result.exception,
        rc=result.exit_code,
        result=result,
        runner=result.runner,
        stderr=result.stderr,
        stderr_bytes=result.stderr_bytes,
        stdout=result.stdout,
        stdout_bytes=result.stdout_bytes,
    )


@pytest.fixture()
def clirun(request: SubRequest) -> Result:
    """Invoke cli.

    Examples:
        >>> @pytest.mark.parametrize("clirun", [["command", "--option"]], indirect=True)
        ... def test_current(clirun: Result):
        ...    assert clirun.exit_code == 0
        ...    assert clirun.stdout == "main"
    """
    return runner.invoke(request.param[0], request.param[1:], catch_exceptions=False)


@pytest.fixture(scope="session")
def local(request: FixtureRequest) -> bool:
    """Fixture to see if or --local passed to pytest or DOCKER. or CI.

    Examples:
        pytest --local
        pytest --local tests/test_fixture.py::test_fixture_local
        pytest tests/test_fixture.py  # docker -> 2 skipped
        pytest tests/test_fixture.py  # 0 skipped
    """
    return request.config.getoption('local', False) or DOCKER or CI or in_tox()


@pytest.fixture(scope="session")
def logger(request: FixtureRequest) -> bool:
    """To show log for fixtures.

    Examples:
        pytest --logger
    """
    return request.config.getoption('logger', False)


@pytest.hookimpl
def pytest_addoption(parser: Parser) -> None:
    """Use config local to skip tests.

    Example:
        >>> @skip_docker
        ... def test_func_docker(local: bool):
        ...     assert local is False
        >>> @pytest.mark.skipif("config.getoption('local') is True", reason='--local option provided')
        ... def test_func_docker(local: bool):
        ...     assert local is False
    """
    with contextlib.suppress(ValueError):
        # when installed pytest_addoption is executed by load_setuptools_entrypoints
        parser.addoption('--local', action='store_true', dest="local", default=False, help='Run local tests.')
        parser.addoption('--logger', action='store_true', dest="logger", default=False, help='Show fixtures log.')


# noinspection PyUnusedLocal
@pytest.hookimpl
def pytest_collection_modifyitems(items: list[nodes.Item], config: Config) -> None:
    """Pytest_collection_modifyitems. config.option.local = True."""


@pytest.hookimpl
def pytest_configure(config: Config) -> None:
    """Pytest configure. config.option.local = True."""
    if DOCKER or CI:
        config.option.local = True


# noinspection PyUnusedLocal
@pytest.hookimpl
def pytest_generate_tests(metafunc: Metafunc) -> None:
    """This is called for every test. Only get/set command line arguments. metafunc.config.option.local = True."""


# noinspection PyUnusedLocal
@pytest.hookimpl
def pytest_sessionstart(session: Session) -> None:
    """Pytest session start: session.config.option.local = True."""


@pytest.fixture()
def repos(tmp_path: Path, logger: bool) -> Generator[Repos]:
    """Provides an instance of :class:`nodeps._repo.Repo` for a local and a remote repository."""
    git_config_global()
    tmp = tmp_path / "repos"
    l = Repo.init(tmp / "local", initial_branch="main")
    remote = Repo.init(tmp / "remote.git", bare=True)
    l.create_remote('origin', remote.git_dir)
    origin = l.remote(name='origin')
    top = Path(l.top)
    top.touch("README.md")
    l.git.add(".")
    l.git.commit("-a", "-m", "First commit.")
    l.git.push("--set-upstream", "origin", "main")
    origin.push()
    clone = remote.clone(tmp / "clone", branch="main")

    if logger:
        LOGGER.setLevel(logging.DEBUG)
        LOGGER.debug(f"clone: {clone.top}")  # noqa: G004
        LOGGER.debug(f"local: {top}")  # noqa: G004
        LOGGER.debug(f"remote: {remote.top}")  # noqa: G004

    yield Repos(clone=clone, local=l, remote=remote)

    shutil.rmtree(tmp, ignore_errors=True)


@pytest.fixture(scope="session")
def rootpath(request: FixtureRequest) -> Path:
    """The path to the :ref:`rootdir <rootdir>`."""
    return Path(request.config.rootpath)


skip_docker = pytest.mark.skipif(
    "config.getoption('local', False) is True",
    reason="--local option or DOCKER or CI or tox",
)
