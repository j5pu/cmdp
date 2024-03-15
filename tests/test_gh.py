import pytest
import typer
from typer.testing import CliRunner

from nodeps import Gh
from nodeps import Path
from nodeps import CI
from nodeps import DOCKER
from nodeps.__main__ import (
    gh_g,
    _commit,
    _next,
    _latest,
    _pull,
    _push,
    _secrets,
    _secrets_names,
    _remote,
    project_p,
    _superproject,
)
from nodeps.fixtures import Repos, repos

runner = CliRunner(mix_stderr=False)


def invoke(app: typer.Typer, args: list[str]):
    return runner.invoke(app, args, catch_exceptions=False)


def test_commit(repos: Repos):
    def touch(n):
        Path(repos.local.top).touch(f"test{n}.text")

    local = Gh(repos.local)

    assert local.latest() == "0.0.0"
    touch(1)
    assert local.status().dirty is True
    local.commit()
    assert local.next() == "0.0.1"
    assert local.status().dirty is False

    touch(2)
    assert local.status().dirty is True
    assert invoke(gh_g, ["commit", str(repos.local.top), "-m", "Feat:"]).exit_code == 0
    assert invoke(gh_g, ["next", str(repos.local.top)]).stdout == "0.1.0\n"
    assert local.status().dirty is False

    touch(3)
    assert local.status().dirty is True
    assert invoke(project_p, ["commit", str(repos.local.top), "--message", "Breaking change:"]).exit_code == 0
    assert invoke(project_p, ["next", str(repos.local.top)]).stdout == "1.0.0\n"
    assert local.status().dirty is False

    touch(4)
    assert local.status().dirty is True
    assert invoke(_commit, [str(repos.local.top), "--msg", "feat:"]).exit_code == 0
    assert invoke(_next, [str(repos.local.top)]).stdout == "1.0.0\n"
    assert local.status().dirty is False


def test_latest(repos: Repos):
    local = Gh(repos.local)

    assert local.latest() == "0.0.0"
    assert invoke(gh_g, ["latest", str(repos.local.top)]).stdout == "0.0.0\n"
    assert invoke(project_p, ["latest", str(repos.local.top)]).stdout == "0.0.0\n"
    assert invoke(_latest, [str(repos.local.top)]).stdout == "0.0.0\n"


def test_next(repos: Repos):
    local = Gh(repos.local)

    assert local.next() == "0.0.0"
    assert invoke(gh_g, ["next", str(repos.local.top)]).stdout == "0.0.0\n"
    assert invoke(project_p, ["next", str(repos.local.top)]).stdout == "0.0.0\n"
    assert invoke(_next, [str(repos.local.top)]).stdout == "0.0.0\n"

    assert local.next(force=True) == "0.0.1"
    assert invoke(gh_g, ["next", str(repos.local.top), "--force", "--part", "MINOR"]).stdout == "0.1.0\n"
    assert invoke(project_p, ["next", str(repos.local.top), "--force", "--part", "MAJOR"]).stdout == "1.0.0\n"
    local.tag("1.0.0")
    assert invoke(_next, [str(repos.local.top), "--force"]).stdout == "1.0.1\n"


def test_pull(repos: Repos):
    def push(n):
        Path(repos.clone.top).touch(f"test{n}.text")
        clone = Gh(repos.clone)
        clone.commit()
        clone.push()

    local = Gh(repos.local)

    push(1)
    assert local.status().pull is True
    local.pull()
    assert local.status().pull is False

    push(2)
    assert local.status().pull is True
    assert invoke(gh_g, ["pull", str(repos.local.top)]).exit_code == 0
    assert local.status().pull is False

    push(3)
    assert local.status().pull is True
    assert invoke(project_p, ["pull", str(repos.local.top)]).exit_code == 0
    assert local.status().pull is False

    push(4)
    assert local.status().pull is True
    assert invoke(_pull, [str(repos.local.top)]).exit_code == 0
    assert local.status().pull is False


def test_push(repos: Repos):
    def commit(n):
        Path(repos.local.top).touch(f"test{n}.text")
        local.commit()

    local = Gh(repos.local)

    commit(1)
    assert local.status().push is True
    local.push()
    assert local.status().push is False

    commit(2)
    assert local.status().push is True
    assert invoke(gh_g, ["push", str(repos.local.top)]).exit_code == 0
    assert local.status().push is False

    commit(3)
    assert local.status().push is True
    assert invoke(project_p, ["push", str(repos.local.top)]).exit_code == 0
    assert local.status().push is False

    commit(4)
    assert local.status().push is True
    assert invoke(_push, [str(repos.local.top)]).exit_code == 0
    assert local.status().push is False


def test_remote(repos: Repos):
    rv = invoke(gh_g, ["remote", str(repos.local.top)])
    assert rv.exit_code == 0
    assert rv.stdout

    rv = invoke(project_p, ["remote", str(repos.local.top)])
    assert rv.exit_code == 0
    assert rv.stdout

    rv = invoke(_remote, [str(repos.local.top)])
    assert rv.exit_code == 0
    assert rv.stdout


@pytest.mark.skipif(CI or DOCKER, reason="secrets: must be local")
def test_secrets():
    assert invoke(gh_g, ["secrets"]).exit_code == 0
    assert "TOKEN" in invoke(gh_g, ["secrets-names"]).stdout.splitlines()

    assert invoke(gh_g, ["secrets"]).exit_code == 0
    assert "TOKEN" in invoke(gh_g, ["secrets-names"]).stdout.splitlines()

    assert invoke(_secrets, []).exit_code == 0
    assert "TOKEN" in invoke(_secrets_names, []).stdout.splitlines()


def test_superproject(repos: Repos):
    local = Gh(repos.local)

    assert local.top

    rv = invoke(gh_g, ["superproject", str(repos.local.top)])
    assert rv.exit_code == 0
    assert rv.stdout

    rv = invoke(project_p, ["superproject", str(repos.local.top)])
    assert rv.exit_code == 0
    assert rv.stdout

    rv = invoke(_superproject, [str(repos.local.top)])
    assert rv.exit_code == 0
    assert rv.stdout


def test_sync(repos: Repos):
    local = Gh(repos.local)

    status = local.status()
    assert status.dirty == status.diverge == status.pull == status.push is False

    assert invoke(gh_g, ["sync", str(repos.local.top)]).exit_code == 0
    assert invoke(project_p, ["sync", str(repos.local.top)]).exit_code == 0

    Path(repos.local.top).touch("test.text")

    status = local.status()
    assert status.dirty is True
    assert status.diverge == status.pull == status.push is False

    assert invoke(gh_g, ["sync", str(repos.local.top)]).exit_code == 0
    assert invoke(project_p, ["sync", str(repos.local.top)]).exit_code == 0

    status = local.status()
    assert status.dirty == status.diverge == status.pull == status.push is False

    Path(repos.clone.top).touch("test1.text")
    clone = Gh(repos.clone)
    status = clone.status()
    assert status.dirty == status.diverge == status.pull is True
    assert status.push is False

    with pytest.raises(RuntimeError):
        # Diverged
        assert invoke(gh_g, ["sync", str(repos.clone.top)]).exit_code == 0

    clone.pull(force=True)
    clone.push()
    status = clone.status()
    assert status.dirty == status.diverge == status.pull == status.push is False

    status = local.status()
    assert status.pull is True
    assert status.dirty == status.diverge == status.push is False

    assert invoke(gh_g, ["sync", str(repos.local.top)]).exit_code == 0
    assert invoke(project_p, ["sync", str(repos.local.top)]).exit_code == 0

    status = local.status()
    assert status.dirty == status.diverge == status.pull == status.push is False

    Path(repos.local.top).touch("test3.text")
    local.commit()

    status = local.status()
    assert status.dirty == status.diverge == status.pull is False
    assert status.push is True

    assert invoke(gh_g, ["sync", str(repos.local.top)]).exit_code == 0
    assert invoke(project_p, ["sync", str(repos.local.top)]).exit_code == 0

    status = local.status()
    assert status.dirty == status.diverge == status.pull == status.push is False


def test_tag(repos: Repos):
    local = Gh(repos.local)

    local.tag("0.1.0")
    assert local.latest() == "0.1.0"

    assert invoke(gh_g, ["tag", "0.1.0", str(repos.local.top)]).exit_code == 0
    assert invoke(gh_g, ["latest", str(repos.local.top)]).stdout == "0.1.0\n"

    assert invoke(project_p, ["tag", "0.1.0", str(repos.local.top)]).exit_code == 0
    assert invoke(project_p, ["latest", str(repos.local.top)]).stdout == "0.1.0\n"


def test_top(repos: Repos):
    local = Gh(repos.local)

    assert local.top

    rv = invoke(gh_g, ["top", str(repos.local.top)])
    assert rv.exit_code == 0
    assert rv.stdout

    rv = invoke(project_p, ["top", str(repos.local.top)])
    assert rv.exit_code == 0
    assert rv.stdout
