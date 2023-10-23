import typer
from typer.testing import CliRunner

from nodeps import Gh
from nodeps.__main__ import *
from nodeps.fixtures import Repos, repos

runner = CliRunner(mix_stderr=False)


def invoke(app: typer.Typer, args: list[str]):
    return runner.invoke(app, args, catch_exceptions=False)


def test_dirty(repos: Repos):
    local = Gh(repos.local.top)
    assert local.dirty() is False
    assert invoke(gh_g, ["dirty", str(repos.local.top)]).exit_code == 1
    assert invoke(project_p, ["dirty", str(repos.local.top)]).exit_code == 1
    assert invoke(_dirty, [str(repos.local.top)]).exit_code == 1
