import pytest

from nodeps.__main__ import gh_g
from nodeps.fixtures import Cli


@pytest.mark.parametrize("cli", [[gh_g, "admin"]], indirect=True)
def test_admin(cli: Cli):
    assert cli.result.exit_code == 0


@pytest.mark.parametrize("cli", [[gh_g, "admin", "--user", "foo"]], indirect=True)
def test_admin_foo(cli: Cli):
    assert cli.result.exit_code == 1


@pytest.mark.parametrize("cli", [[gh_g, "branch"]], indirect=True)
def test_branch(cli: Cli):
    assert cli.result.exit_code == 0
    assert cli.result.stdout == "main\n"


@pytest.mark.parametrize("cli", [[gh_g, "current"]], indirect=True)
def test_current(cli: Cli):
    assert cli.result.exit_code == 0
    assert cli.result.stdout == "main\n"


@pytest.mark.parametrize("cli", [[gh_g, "default"]], indirect=True)
def test_default(cli: Cli):
    assert cli.result.exit_code == 0
    assert cli.result.stdout == "main\n"


@pytest.mark.parametrize("cli", [[gh_g, "github"]], indirect=True)
def test_github(cli: Cli):
    assert cli.result.exit_code == 0
    assert cli.result.stdout


@pytest.mark.parametrize("cli", [[gh_g, "public"]], indirect=True)
def test_public(cli: Cli):
    assert cli.result.exit_code == 0
