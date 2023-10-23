import typer
from typer.testing import CliRunner

from nodeps import Gh
from nodeps import Path
from nodeps.__main__ import *
from nodeps.fixtures import Repos, repos

runner = CliRunner(mix_stderr=False)


def invoke(app: typer.Typer, args: list[str]):
    return runner.invoke(app, args, catch_exceptions=False)


def test_status(repos: Repos):
    local = Gh(repos.local.top)

    # <editor-fold desc="Clean">
    status = local.status()

    assert status.dirty == status.diverge == status.pull == status.push is False

    assert invoke(gh_g, ["dirty", str(repos.local.top)]).exit_code == 1
    assert invoke(project_p, ["dirty", str(repos.local.top)]).exit_code == 1
    assert invoke(_dirty, [str(repos.local.top)]).exit_code == 1

    assert invoke(gh_g, ["diverge", str(repos.local.top)]).exit_code == 1
    assert invoke(project_p, ["diverge", str(repos.local.top)]).exit_code == 1
    assert invoke(_diverge, [str(repos.local.top)]).exit_code == 1

    assert invoke(gh_g, ["needpull", str(repos.local.top)]).exit_code == 1
    assert invoke(project_p, ["needpull", str(repos.local.top)]).exit_code == 1
    assert invoke(_needpull, [str(repos.local.top)]).exit_code == 1

    assert invoke(gh_g, ["needpush", str(repos.local.top)]).exit_code == 1
    assert invoke(project_p, ["needpush", str(repos.local.top)]).exit_code == 1
    assert invoke(_needpush, [str(repos.local.top)]).exit_code == 1
    # </editor-fold>

    # <editor-fold desc="Dirty">
    Path(repos.local.top).touch("test.text")

    status = local.status()

    assert status.dirty is True
    assert status.diverge == status.pull == status.push is False

    assert invoke(gh_g, ["dirty", str(repos.local.top)]).exit_code == 0
    assert invoke(project_p, ["dirty", str(repos.local.top)]).exit_code == 0
    assert invoke(_dirty, [str(repos.local.top)]).exit_code == 0

    assert invoke(gh_g, ["diverge", str(repos.local.top)]).exit_code == 1
    assert invoke(project_p, ["diverge", str(repos.local.top)]).exit_code == 1
    assert invoke(_diverge, [str(repos.local.top)]).exit_code == 1

    assert invoke(gh_g, ["needpull", str(repos.local.top)]).exit_code == 1
    assert invoke(project_p, ["needpull", str(repos.local.top)]).exit_code == 1
    assert invoke(_needpull, [str(repos.local.top)]).exit_code == 1

    assert invoke(gh_g, ["needpush", str(repos.local.top)]).exit_code == 1
    assert invoke(project_p, ["needpush", str(repos.local.top)]).exit_code == 1
    assert invoke(_needpush, [str(repos.local.top)]).exit_code == 1
    # </editor-fold>

    # <editor-fold desc="Need Pull & Diverge">
    Path(repos.clone.top).touch("test.text")
    repos.clone.git.add(".")
    repos.clone.git.commit("-a", "-m", "First commit.")
    repos.clone.git.push("--set-upstream", "origin", "main")
    origin = repos.clone.remote(name='origin')
    origin.push()

    status = local.status()
    assert status.dirty == status.diverge == status.pull is True
    assert status.push is False

    assert invoke(gh_g, ["dirty", str(repos.local.top)]).exit_code == 0
    assert invoke(project_p, ["dirty", str(repos.local.top)]).exit_code == 0
    assert invoke(_dirty, [str(repos.local.top)]).exit_code == 0

    assert invoke(gh_g, ["diverge", str(repos.local.top)]).exit_code == 0
    assert invoke(project_p, ["diverge", str(repos.local.top)]).exit_code == 0
    assert invoke(_diverge, [str(repos.local.top)]).exit_code == 0

    assert invoke(gh_g, ["needpull", str(repos.local.top)]).exit_code == 0
    assert invoke(project_p, ["needpull", str(repos.local.top)]).exit_code == 0
    assert invoke(_needpull, [str(repos.local.top)]).exit_code == 0

    assert invoke(gh_g, ["needpush", str(repos.local.top)]).exit_code == 1
    assert invoke(project_p, ["needpush", str(repos.local.top)]).exit_code == 1
    assert invoke(_needpush, [str(repos.local.top)]).exit_code == 1
    # </editor-fold>

    # <editor-fold desc="Need Push & Pull & Diverge">
    repos.local.git.add(".")
    repos.local.git.commit("-a", "-m", "First commit.")

    status = local.status()

    assert status.diverge == status.pull == status.push is True
    assert status.dirty is False

    assert invoke(gh_g, ["dirty", str(repos.local.top)]).exit_code == 1
    assert invoke(project_p, ["dirty", str(repos.local.top)]).exit_code == 1
    assert invoke(_dirty, [str(repos.local.top)]).exit_code == 1

    assert invoke(gh_g, ["diverge", str(repos.local.top)]).exit_code == 0
    assert invoke(project_p, ["diverge", str(repos.local.top)]).exit_code == 0
    assert invoke(_diverge, [str(repos.local.top)]).exit_code == 0

    assert invoke(gh_g, ["needpull", str(repos.local.top)]).exit_code == 0
    assert invoke(project_p, ["needpull", str(repos.local.top)]).exit_code == 0
    assert invoke(_needpull, [str(repos.local.top)]).exit_code == 0

    assert invoke(gh_g, ["needpush", str(repos.local.top)]).exit_code == 0
    assert invoke(project_p, ["needpush", str(repos.local.top)]).exit_code == 0
    assert invoke(_needpush, [str(repos.local.top)]).exit_code == 0
    # </editor-fold>

    # <editor-fold desc="Need Push">
    origin = repos.local.remote(name='origin')
    origin.pull()

    status = local.status()

    assert status.dirty == status.diverge == status.pull is False
    assert status.push is True

    assert invoke(gh_g, ["dirty", str(repos.local.top)]).exit_code == 1
    assert invoke(project_p, ["dirty", str(repos.local.top)]).exit_code == 1
    assert invoke(_dirty, [str(repos.local.top)]).exit_code == 1

    assert invoke(gh_g, ["diverge", str(repos.local.top)]).exit_code == 1
    assert invoke(project_p, ["diverge", str(repos.local.top)]).exit_code == 1
    assert invoke(_diverge, [str(repos.local.top)]).exit_code == 1

    assert invoke(gh_g, ["needpull", str(repos.local.top)]).exit_code == 1
    assert invoke(project_p, ["needpull", str(repos.local.top)]).exit_code == 1
    assert invoke(_needpull, [str(repos.local.top)]).exit_code == 1

    assert invoke(gh_g, ["needpush", str(repos.local.top)]).exit_code == 0
    assert invoke(project_p, ["needpush", str(repos.local.top)]).exit_code == 0
    assert invoke(_needpush, [str(repos.local.top)]).exit_code == 0
    # </editor-fold>

    # <editor-fold desc="Clean">
    origin = repos.local.remote(name='origin')
    origin.push()

    status = local.status()

    assert status.dirty == status.diverge == status.pull == status.push is False

    assert invoke(gh_g, ["dirty", str(repos.local.top)]).exit_code == 1
    assert invoke(project_p, ["dirty", str(repos.local.top)]).exit_code == 1
    assert invoke(_dirty, [str(repos.local.top)]).exit_code == 1

    assert invoke(gh_g, ["diverge", str(repos.local.top)]).exit_code == 1
    assert invoke(project_p, ["diverge", str(repos.local.top)]).exit_code == 1
    assert invoke(_diverge, [str(repos.local.top)]).exit_code == 1

    assert invoke(gh_g, ["needpull", str(repos.local.top)]).exit_code == 1
    assert invoke(project_p, ["needpull", str(repos.local.top)]).exit_code == 1
    assert invoke(_needpull, [str(repos.local.top)]).exit_code == 1

    assert invoke(gh_g, ["needpush", str(repos.local.top)]).exit_code == 1
    assert invoke(project_p, ["needpush", str(repos.local.top)]).exit_code == 1
    assert invoke(_needpush, [str(repos.local.top)]).exit_code == 1
    # </editor-fold>
