import subprocess

from nodeps import DOCKER, PY_MAJOR_MINOR
from nodeps.fixtures import skip_docker


@skip_docker
def test_docker(pytestconfig):
    assert DOCKER is False
    assert subprocess.run(f"{pytestconfig.rootpath}/docker/docker.sh {PY_MAJOR_MINOR}", shell=True).returncode == 0
