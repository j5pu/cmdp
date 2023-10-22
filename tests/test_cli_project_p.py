from pathlib import Path

import pytest

from nodeps.__main__ import project_p
from nodeps import NODEPS_PROJECT_NAME


@pytest.mark.parametrize("invoke", [[project_p, "admin"]], indirect=True)
def test_admin(invoke):
    assert invoke.exit_code == 0


@pytest.mark.parametrize("invoke", [[project_p, "admin", "--user", "foo"]], indirect=True)
def test_admin_foo(invoke):
    assert invoke.exit_code == 1


@pytest.mark.parametrize("invoke", [[project_p, "branch"]], indirect=True)
def test_branch(invoke):
    assert invoke.exit_code == 0
    assert invoke.stdout


@pytest.mark.parametrize("invoke", [[project_p, "build"]], indirect=True)
def test_build(invoke):
    assert invoke.exit_code == 0


@pytest.mark.parametrize("invoke", [[project_p, "build", str(Path(__file__))]], indirect=True)
def test_build_path(invoke):
    assert invoke.exit_code == 0


@pytest.mark.parametrize("invoke", [[project_p, "build", NODEPS_PROJECT_NAME]], indirect=True)
def test_build_name(invoke):
    assert invoke.exit_code == 0


@pytest.mark.parametrize("invoke", [[project_p, "builds"]], indirect=True)
def test_builds(invoke):
    assert invoke.exit_code == 0


@pytest.mark.parametrize("invoke", [[project_p, "buildrequires"]], indirect=True)
def test_buildrequires(invoke):
    assert invoke.exit_code == 0


@pytest.mark.parametrize("invoke", [[project_p, "commit"]], indirect=True)
def test_commit(invoke):
    assert invoke.exit_code == 0


@pytest.mark.parametrize("invoke", [[project_p, "dependencies"]], indirect=True)
def test_dependencies(invoke):
    assert invoke.exit_code == 0


@pytest.mark.parametrize("invoke", [[project_p, "distribution"]], indirect=True)
def test_dependencies(invoke):
    assert invoke.exit_code == 0


@pytest.mark.parametrize("invoke", [[project_p, "extras"]], indirect=True)
def test_extras(invoke):
    assert invoke.exit_code == 0


@pytest.mark.parametrize("invoke", [[project_p, "ipythondir"]], indirect=True)
def test_ipythondir(invoke):
    assert invoke.exit_code == 0
    assert "ipython_profile" in invoke.stdout


@pytest.mark.parametrize("invoke", [[project_p, "latest"]], indirect=True)
def test_latest(invoke):
    assert invoke.exit_code == 0


@pytest.mark.parametrize("invoke", [[project_p, "mip"]], indirect=True)
def test_mip(invoke):
    assert invoke.exit_code == 0
    assert "." in invoke.stdout


@pytest.mark.parametrize("invoke", [[project_p, "next"]], indirect=True)
def test_next(invoke):
    assert invoke.exit_code == 0


@pytest.mark.parametrize("invoke", [[project_p, "public"]], indirect=True)
def test_public(invoke):
    assert invoke.exit_code == 0


@pytest.mark.parametrize("invoke", [[project_p, "pythonstartup"]], indirect=True)
def test_pythonstartup(invoke):
    assert invoke.exit_code == 0
    assert "python_startup" in invoke.stdout


@pytest.mark.parametrize("invoke", [[project_p, "remote"]], indirect=True)
def test_remote(invoke):
    assert invoke.exit_code == 0
    assert "https://" in invoke.stdout


@pytest.mark.parametrize("invoke", [[project_p, "repos"]], indirect=True)
def test_repos(invoke):
    assert invoke.exit_code == 0


@pytest.mark.parametrize("invoke", [[project_p, "sha"]], indirect=True)
def test_sha(invoke):
    assert invoke.exit_code == 0


@pytest.mark.parametrize("invoke", [[project_p, "superproject"]], indirect=True)
def test_superproject(invoke):
    assert invoke.exit_code == 0


@pytest.mark.parametrize("invoke", [[project_p, "top"]], indirect=True)
def test_top(invoke):
    assert invoke.exit_code == 0


@pytest.mark.parametrize("invoke", [[project_p, "version"]], indirect=True)
def test_version(invoke):
    assert invoke.exit_code == 0


@pytest.mark.parametrize("invoke", [[project_p, "venv"]], indirect=True)
def test_venv(invoke):
    assert invoke.exit_code == 0
