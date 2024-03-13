from pathlib import Path

import pytest

from nodeps import IPYTHONDIR
from nodeps import PYTHONSTARTUP
from nodeps.__main__ import project_p
from nodeps import NODEPS_PROJECT_NAME
from nodeps.fixtures import Cli


@pytest.mark.parametrize("cli", [[project_p, "admin"]], indirect=True)
def test_admin(cli: Cli):
    assert cli.result.exit_code == 0


@pytest.mark.parametrize("cli", [[project_p, "admin", "--user", "foo"]], indirect=True)
def test_admin_foo(cli: Cli):
    assert cli.result.exit_code == 1


@pytest.mark.parametrize("cli", [[project_p, "branch"]], indirect=True)
def test_branch(cli: Cli):
    assert cli.result.exit_code == 0
    assert cli.result.stdout == "main\n"


@pytest.mark.parametrize("cli", [[project_p, "build"]], indirect=True)
def test_build(cli: Cli):
    assert cli.result.exit_code == 0


@pytest.mark.parametrize("cli", [[project_p, "build", str(Path(__file__))]], indirect=True)
def test_build_path(cli: Cli):
    assert cli.result.exit_code == 0


@pytest.mark.parametrize("cli", [[project_p, "build", NODEPS_PROJECT_NAME]], indirect=True)
def test_build_name(cli: Cli):
    assert cli.result.exit_code == 0


@pytest.mark.parametrize("cli", [[project_p, "builds"]], indirect=True)
def test_builds(cli: Cli):
    assert cli.result.exit_code == 0


@pytest.mark.parametrize("cli", [[project_p, "buildrequires"]], indirect=True)
def test_buildrequires(cli: Cli):
    assert cli.result.exit_code == 0


@pytest.mark.parametrize("cli", [[project_p, "current"]], indirect=True)
def test_current(cli: Cli):
    assert cli.result.exit_code == 0
    assert cli.result.stdout == "main\n"


@pytest.mark.parametrize("cli", [[project_p, "default"]], indirect=True)
def test_default(cli: Cli):
    assert cli.result.exit_code == 0
    assert cli.result.stdout == "main\n"


@pytest.mark.parametrize("cli", [[project_p, "dependencies"]], indirect=True)
def test_dependencies(cli: Cli):
    assert cli.result.exit_code == 0


@pytest.mark.parametrize("cli", [[project_p, "distribution"]], indirect=True)
def test_dependencies(cli: Cli):
    assert cli.result.exit_code == 0


@pytest.mark.parametrize("cli", [[project_p, "extras"]], indirect=True)
def test_extras(cli: Cli):
    assert cli.result.exit_code == 0


@pytest.mark.parametrize("cli", [[project_p, "github"]], indirect=True)
def test_github(cli: Cli):
    assert cli.result.exit_code == 0
    assert cli.result.stdout


@pytest.mark.parametrize("cli", [[project_p, "ipythondir"]], indirect=True)
def test_ipythondir(cli: Cli):
    assert cli.exit_code == 0
    assert str(IPYTHONDIR) == cli.stdout.strip("\n")


@pytest.mark.parametrize("cli", [[project_p, "latest"]], indirect=True)
def test_latest(cli: Cli):
    assert cli.result.exit_code == 0


@pytest.mark.parametrize("cli", [[project_p, "mip"]], indirect=True)
def test_mip(cli: Cli):
    assert cli.result.exit_code == 0
    assert "." in cli.result.stdout


@pytest.mark.parametrize("cli", [[project_p, "next"]], indirect=True)
def test_next(cli: Cli):
    assert cli.result.exit_code == 0


@pytest.mark.parametrize("cli", [[project_p, "public"]], indirect=True)
def test_public(cli: Cli):
    assert cli.result.exit_code == 0


@pytest.mark.parametrize("cli", [[project_p, "pythonstartup"]], indirect=True)
def test_pythonstartup(cli: Cli):
    assert cli.result.exit_code == 0
    assert str(PYTHONSTARTUP) == cli.stdout.strip("\n")


@pytest.mark.parametrize("cli", [[project_p, "remote"]], indirect=True)
def test_remote(cli: Cli):
    assert cli.result.exit_code == 0
    assert "https://" in cli.result.stdout


@pytest.mark.parametrize("cli", [[project_p, "repos"]], indirect=True)
def test_repos(cli: Cli):
    assert cli.result.exit_code == 0


@pytest.mark.parametrize("cli", [[project_p, "superproject"]], indirect=True)
def test_superproject(cli: Cli):
    assert cli.result.exit_code == 0


@pytest.mark.parametrize("cli", [[project_p, "top"]], indirect=True)
def test_top(cli: Cli):
    assert cli.result.exit_code == 0


@pytest.mark.parametrize("cli", [[project_p, "version"]], indirect=True)
def test_version(cli: Cli):
    assert cli.result.exit_code == 0


@pytest.mark.parametrize("cli", [[project_p, "venv"]], indirect=True)
def test_venv(cli: Cli):
    assert cli.result.exit_code == 0
