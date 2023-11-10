import pytest
from typer.testing import CliRunner

from nodeps.fixtures import *

runner = CliRunner(mix_stderr=False)


def pytest_addoption(parser):
    parser.addoption('--local', action='store_true', default=False, help='Run local tests.')


@pytest.fixture
def local(request):
    return request.config.getoption('--local')


@pytest.fixture()
def invoke(request):
    return runner.invoke(request.param[0], request.param[1:], catch_exceptions=False)
