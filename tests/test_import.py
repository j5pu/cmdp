import subprocess

import nodeps

from nodeps import EXECUTABLE_SITE, NODEPS_NAME, NODEPS_SRC, Path


def test_import() -> None:
    """Test that the package can be imported."""
    assert isinstance(nodeps.__name__, str)
    with Path.tempfile() as tmp:
        tmp.write_text(f"import sys; sys.path.insert(0, '{str(NODEPS_SRC)}'); import {NODEPS_NAME}")
        assert subprocess.run([EXECUTABLE_SITE, tmp], check=True).returncode == 0
