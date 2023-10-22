import pytest

from nodeps.__main__ import gh_g


@pytest.mark.parametrize("invoke", [[gh_g, "admin"]], indirect=True)
def test_admin(invoke):
    assert invoke.exit_code == 0


@pytest.mark.parametrize("invoke", [[gh_g, "admin", "--user", "foo"]], indirect=True)
def test_admin_foo(invoke):
    assert invoke.exit_code == 1


@pytest.mark.parametrize("invoke", [[gh_g, "public"]], indirect=True)
def test_public(invoke):
    assert invoke.exit_code == 0
