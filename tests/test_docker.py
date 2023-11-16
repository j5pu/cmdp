import pathlib
import subprocess

from nodeps import DOCKER_COMMAND, PY_MAJOR_MINOR
from nodeps.fixtures import skip_docker


@skip_docker
def test_docker(pytestconfig):
    assert DOCKER_COMMAND is True
    assert subprocess.run(f"{pytestconfig.rootpath}/docker/docker.sh {PY_MAJOR_MINOR}", shell=True).returncode == 0
