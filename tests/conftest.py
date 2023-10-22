import pytest
from typer.testing import CliRunner

from nodeps.fixtures import *

runner = CliRunner(mix_stderr=False)


@pytest.fixture()
def invoke(request):
    return runner.invoke(request.param[0], request.param[1:], catch_exceptions=False)
