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

from nodeps import Path
from nodeps.extras._repo import Repo

LOGGER = logging.getLogger(__name__)


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
def repos(tmp_path: Path) -> Generator[Repos]:
    """Provides an instance of :class:`nodeps._repo.Repo` for a local and a remote repository."""
    tmp = tmp_path / "repos"
    local = Repo.init(tmp / "local")
    remote = Repo.init(tmp / "remote.git", bare=True)
    local.create_remote('origin', remote.git_dir)
    origin = local.remote(name='origin')
    top = Path(local.top)
    top.touch("README.md")
    local.git.add(".")
    local.git.commit("-a", "-m", "First commit.")
    local.git.push("--set-upstream", "origin", "main")
    origin.push()
    clone = remote.clone(tmp / "clone")

    LOGGER.debug(f"clone: {clone.top}")  # noqa: G004
    LOGGER.debug(f"local: {top}")  # noqa: G004
    LOGGER.debug(f"remote: {remote.top}")  # noqa: G004

    yield Repos(clone=clone, local=local, remote=remote)

    shutil.rmtree(tmp, ignore_errors=True)
