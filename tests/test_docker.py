import os
import subprocess

import pytest

from nodeps import DOCKER_COMMAND, NODEPS_PATH, PY_MAJOR_MINOR


@pytest.mark.skipif(not DOCKER_COMMAND, reason="running already in a container")
def test_docker():
    assert DOCKER_COMMAND is True
    path = NODEPS_PATH.parent.parent
    tag = f"tests-{path.name}"
    assert subprocess.run(
        f"docker build --build-arg='PY_VERSION={PY_MAJOR_MINOR}' --quiet -f {path / 'tests.dockerfile'} -t {tag} "
        f"{path} && docker run --rm {tag}", shell=True).returncode == 0
