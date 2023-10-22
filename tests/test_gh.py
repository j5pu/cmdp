import logging
import subprocess

from pytest_git_fixtures import GITRepo  # Optional, for typing

LOGGER = logging.getLogger(__name__)
def log(key, value):
    """Log a key/value pair."""
    LOGGER.info("%s: %s", key, value)

def test_fixture(git_repo: GITRepo) -> None:
    """Test config."""
    log("clone_git_dir", git_repo.clone_git_dir)
    log("clone_work_tree", git_repo.clone_work_tree)
