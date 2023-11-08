import pytest

from nodeps import aioclone
from nodeps import Path


@pytest.mark.asyncio
async def test_aioclone():
    with Path.tempdir() as tmp:
        directory = tmp / "1" / "2" / "3"
        rv = await aioclone("octocat", "Hello-World", path=directory)
        assert rv == directory
        assert (directory / "README").exists()
