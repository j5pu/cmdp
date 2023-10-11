# coding=utf-8
"""
Tests for aioclone.
"""
# FIXME: copied from Archive/shrc/src/shrc

import pytest

from pyrc import aioclone
from pyrc import TempDir


@pytest.mark.asyncio
async def test_aioclone():
    with TempDir() as tmp:
        directory = tmp / "1" / "2" / "3"
        rv = await aioclone("octocat", "Hello-World", path=directory)
        assert rv.returncode == 0
        assert (directory / "README").exists()
