import pytest

from nodeps.__main__ import gh_g


@pytest.mark.parametrize("invoke", [[gh_g, "admin"]], indirect=True)
def test_admin(invoke):
    assert invoke.exit_code == 0


@pytest.mark.parametrize("invoke", [[gh_g, "admin", "--user", "foo"]], indirect=True)
def test_admin_foo(invoke):
    assert invoke.exit_code == 1


@pytest.mark.parametrize("invoke", [[gh_g, "branch"]], indirect=True)
def test_branch(invoke):
    assert invoke.exit_code == 0
    assert invoke.stdout == "main\n"


@pytest.mark.parametrize("invoke", [[gh_g, "current"]], indirect=True)
def test_current(invoke):
    assert invoke.exit_code == 0
    assert invoke.stdout == "main\n"


@pytest.mark.parametrize("invoke", [[gh_g, "default"]], indirect=True)
def test_default(invoke):
    assert invoke.exit_code == 0
    assert invoke.stdout == "main\n"


@pytest.mark.parametrize("invoke", [[gh_g, "github"]], indirect=True)
def test_github(invoke):
    assert invoke.exit_code == 0
    assert invoke.stdout


@pytest.mark.parametrize("invoke", [[gh_g, "public"]], indirect=True)
def test_public(invoke):
    assert invoke.exit_code == 0
