from pathlib import Path

import pytest

from nodeps.__main__ import g


@pytest.mark.parametrize("invoke", [[g, "admin"]], indirect=True)
def test_admin(invoke):
    assert invoke.exit_code == 0

