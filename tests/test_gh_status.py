import typer

from nodeps import Gh
from nodeps import Path
from nodeps.__main__ import _dirty
from nodeps.__main__ import _diverge
from nodeps.__main__ import _needpull
from nodeps.__main__ import _needpush
from nodeps.__main__ import gh_g
from nodeps.__main__ import project_p
from nodeps.fixtures import Repos
from nodeps.fixtures import repos
from nodeps.fixtures import runner


def invoke(app: typer.Typer, args: list[str]):
    return runner.invoke(app, args, catch_exceptions=False)


def sync(local: Gh):
    local.sync()

    status = local.status()
    assert status.dirty == status.diverge == status.pull == status.push is False


def test_clean(repos: Repos):
    local = Gh(repos.local)

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

    sync(local)


def test_dirty(repos: Repos):
    local = Gh(repos.local)

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

    sync(local)


def test_needs_pull(repos: Repos):
    local = Gh(repos.local)

    Path(repos.clone.top).touch("test.text")
    repos.clone.git.add(".")
    repos.clone.git.commit("-a", "-m", "First commit.")
    origin = repos.clone.remote(name='origin')
    origin.push()

    status = local.status()
    assert status.pull is True
    assert status.dirty == status.diverge == status.push is False

    assert invoke(gh_g, ["dirty", str(repos.local.top)]).exit_code == 1
    assert invoke(project_p, ["dirty", str(repos.local.top)]).exit_code == 1
    assert invoke(_dirty, [str(repos.local.top)]).exit_code == 1

    assert invoke(gh_g, ["diverge", str(repos.local.top)]).exit_code == 1
    assert invoke(project_p, ["diverge", str(repos.local.top)]).exit_code == 1
    assert invoke(_diverge, [str(repos.local.top)]).exit_code == 1

    assert invoke(gh_g, ["needpull", str(repos.local.top)]).exit_code == 0
    assert invoke(project_p, ["needpull", str(repos.local.top)]).exit_code == 0
    assert invoke(_needpull, [str(repos.local.top)]).exit_code == 0

    assert invoke(gh_g, ["needpush", str(repos.local.top)]).exit_code == 1
    assert invoke(project_p, ["needpush", str(repos.local.top)]).exit_code == 1
    assert invoke(_needpush, [str(repos.local.top)]).exit_code == 1

    sync(local)


def test_dirty_diverge_needs_pull(repos: Repos):
    local = Gh(repos.local)

    Path(repos.local.top).touch("test_local.text")
    Path(repos.clone.top).touch("test_remote.text")
    repos.clone.git.add(".")
    repos.clone.git.commit("-a", "-m", "First commit.")

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

    Path(repos.local.top).rm("test_local.text")
    sync(local)


def test_diverge_needs_pull_needs_push(repos: Repos):
    local = Gh(repos.local)

    Path(repos.local.top).touch("test_local.text")
    repos.local.git.add(".")
    repos.local.git.commit("-a", "-m", "First commit.")

    Path(repos.clone.top).touch("test_remote.text")
    repos.clone.git.add(".")
    repos.clone.git.commit("-a", "-m", "First commit.")
    origin = repos.clone.remote(name='origin')
    origin.push()

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

    repos.local.git.reset("HEAD~1", soft=True)
    repos.local.git.stash("save", "-u")

    sync(local)


def test_needs_push(repos: Repos):
    local = Gh(repos.local)

    Path(repos.local.top).touch("test_local.text")
    repos.local.git.add(".")
    repos.local.git.commit("-a", "-m", "First commit.")

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

    sync(local)
