"""CLI for nodeps."""
__all__ = (
    "gh_g",
    "project_p",
    "_branch",
    "_browser",
    "_build",
    "_builds",
    "_buildrequires",
    "_clean",
    "_commit",
    "_completions",
    "_current",
    "_dependencies",
    "_dirty",
    "_distribution",
    "_diverge",
    "_docs",
    "_extras",
    "_ipy",
    "_ipythondir",
    "_latest",
    "_mip",
    "_needpull",
    "_needpush",
    "_next",
    "_publish",
    "_pull",
    "_push",
    "_pypi",
    "_pytests",
    "_pythonstartup",
    "_remote",
    "_repos",
    "_requirement",
    "_requirements",
    "_secrets",
    "_secrets_names",
    "_status",
    "_superproject",
    "_tests",
    "_version",
    "_venv",
    "_venvs",
)

import copy
import dataclasses
import sys
from pathlib import Path
from typing import Annotated

from .ipython import IPYTHONDIR, PYTHONSTARTUP, ipy
from .modules import (
    GIT,
    GITHUB_URL,
    NODEPS_EXECUTABLE,
    NODEPS_PROJECT_NAME,
    PYTHON_DEFAULT_VERSION,
    PYTHON_VERSIONS,
    Bump,
    Gh,
    GitUrl,
    Project,
    ProjectRepos,
    dict_sort,
    mip,
    pipmetapathfinder,
)

with pipmetapathfinder():
    import typer.completion


def _scheme_completions(ctx: typer.Context, args: list[str], incomplete: str):
    from rich.console import Console
    console = Console(stderr=True)
    if args:
        console.print(f"{args}")

    valid = list(GITHUB_URL)
    valid.pop(0)
    provided = ctx.params.get("name") or []
    for item in valid:
        if item.startswith(incomplete) and item not in provided:
            yield item


def _repos_completions(ctx: typer.Context, args: list[str], incomplete: str):
    from rich.console import Console
    console = Console(stderr=True)

    if args:
        console.print(f"{args}")

    provided = ctx.params.get("name") or []

    # r = Project().repos(ProjectRepos.DICT)
    # valid = list(r.keys()) + [str(item) for item in r.values()]
    for item in Project().repos():
        if item.startswith(incomplete) and item not in provided:
            yield item


def _versions_completions(ctx: typer.Context, args: list[str], incomplete: str):
    from rich.console import Console

    console = Console(stderr=True)
    if args:
        console.print(f"{args}")
    valid = PYTHON_VERSIONS
    provided = ctx.params.get("name") or []
    for item in valid:
        if item.startswith(incomplete) and item not in provided:
            yield item


_cwd = Path.cwd()
_typer_options = {"add_completion": False, "context_settings": {"help_option_names": ["-h", "--help"]}}

gh_g = typer.Typer(no_args_is_help=True, **_typer_options, name="g")
project_p = typer.Typer(no_args_is_help=True, **_typer_options, name=NODEPS_EXECUTABLE)

_branch = typer.Typer(**_typer_options, name="branch")
_browser = typer.Typer(**_typer_options, name="browser")
_build = typer.Typer(**_typer_options, name="build")
_builds = typer.Typer(**_typer_options, name="builds")
_buildrequires = typer.Typer(**_typer_options, name="buildrequires")
_clean = typer.Typer(**_typer_options, name="clean")
_commit = typer.Typer(**_typer_options, name="commit")
_completions = typer.Typer(**_typer_options, name="completions")
_current = typer.Typer(**_typer_options, name="current")
_dependencies = typer.Typer(**_typer_options, name="dependencies")
_dirty = typer.Typer(**_typer_options, name="dirty")
_distribution = typer.Typer(**_typer_options, name="distribution")
_diverge = typer.Typer(**_typer_options, name="diverge")
_docs = typer.Typer(**_typer_options, name="docs")
_extras = typer.Typer(**_typer_options, name="extras")
_ipy = typer.Typer(**_typer_options, name="ipy")
_ipythondir = typer.Typer(**_typer_options, name="ipythondir")
_latest = typer.Typer(**_typer_options, name="latest")
_mip = typer.Typer(**_typer_options, name="mip")
_needpull = typer.Typer(**_typer_options, name="needpull")
_needpush = typer.Typer(**_typer_options, name="needpush")
_next = typer.Typer(**_typer_options, name="next")
_publish = typer.Typer(**_typer_options, name="publish")
_pull = typer.Typer(**_typer_options, name="pull")
_push = typer.Typer(**_typer_options, name="push")
_pypi = typer.Typer(**_typer_options, name="pypi")
_pytests = typer.Typer(**_typer_options, name="pytests")
_pythonstartup = typer.Typer(**_typer_options, name="pythonstartup")
_remote = typer.Typer(**_typer_options, name="remote")
_repos = typer.Typer(**_typer_options, name="repos")
_requirement = typer.Typer(**_typer_options, name="requirement")
_requirements = typer.Typer(**_typer_options, name="requirements")
_secrets = typer.Typer(**_typer_options, name="secrets")
_secrets_names = typer.Typer(**_typer_options, name="secrets-names")
_status = typer.Typer(**_typer_options, name="status")
_superproject = typer.Typer(**_typer_options, name="superproject")
_tests = typer.Typer(**_typer_options, name="tests")
_version = typer.Typer(**_typer_options, name="version")
_venv = typer.Typer(**_typer_options, name="venv")
_venvs = typer.Typer(**_typer_options, name="venvs")


@gh_g.command(name="admin")
def admin_gh_g(
        data: Annotated[
            Path,  # noqa: RUF013
            typer.Argument(help="Url, path or user (to be used with name), default None for cwd."),
        ] = None,
        repo: str = typer.Option(None, help="Repo name. If not None it will use data as the owner "
                                            "if not None, otherwise $GIT."),
        user: str = typer.Option(GIT, help="user name to check if admin"),
        rm: bool = typer.Option(False, help="Remove cache"),
):
    """Can user admin repository."""
    sys.exit(int(not GitUrl(data=data, repo=repo).admin(user=user, rm=rm)))


@project_p.command(name="admin")
def admin_project_p(
        data: Annotated[
            Path,
            typer.Argument(
                help="Path/file to project or name of project",
                autocompletion=_repos_completions,
            ),
        ] = _cwd,
        user: str = typer.Option(GIT, help="user name to check if admin"),
        rm: bool = typer.Option(False, help="Remove cache"),
):
    """Can user admin repository."""
    sys.exit(int(not Project(data, rm=rm).gh.admin(user=user, rm=rm)))


@gh_g.command(name="branch")
@_branch.command(name="branch")
def branch_gh_g(
        data: Annotated[
            Path,  # noqa: RUF013
            typer.Argument(help="Url, path or user (to be used with name), default None for cwd."),
        ] = None,
        repo: str = typer.Option(None, help="Repo name. If not None it will use data as the owner "
                                            "if not None, otherwise $GIT."),
):
    """Current branch."""
    print(Gh(data=data, repo=repo).current())


@project_p.command("branch")
def branch_project_p(
        data: Annotated[
            Path,
            typer.Argument(
                help="Path/file to project or name of project",
                autocompletion=_repos_completions,
            ),
        ] = _cwd,
        rm: bool = typer.Option(False, help="Remove cache"),
):
    """Current branch."""
    print(Project(data, rm=rm).gh.current())


@project_p.command()
def brew(
        data: Annotated[
            Path,
            typer.Argument(
                help="Path/file to project or name of project",
                autocompletion=_repos_completions,
            ),
        ] = _cwd,
        command: str = typer.Option("", help="Command to check in order to run brew"),
        rm: bool = typer.Option(False, help="Remove cache"),
):
    """Clean project."""
    Project(data, rm=rm).brew(command if command else None)


@project_p.command()
@_browser.command()
def browser(
        data: Annotated[
            Path,
            typer.Argument(
                help="Path/file to project or name of project",
                autocompletion=_repos_completions,
            ),
        ] = _cwd,
        version: Annotated[str, typer.Option(help="python major and minor version",
                                             autocompletion=_versions_completions)] = PYTHON_DEFAULT_VERSION,
        quiet: bool = True,
        rm: bool = typer.Option(False, help="Remove cache"),
):
    """Build and serve the documentation with live reloading on file changes."""
    Project(data, rm=rm).browser(version=version, quiet=quiet)


@project_p.command()
@_build.command()
def build(
        data: Annotated[
            Path,
            typer.Argument(
                help="Path/file to project or name of project",
                autocompletion=_repos_completions,
            ),
        ] = _cwd,
        version: Annotated[str, typer.Option(help="python major and minor version",
                                             autocompletion=_versions_completions)] = PYTHON_DEFAULT_VERSION,
        quiet: bool = True,
        rm: bool = typer.Option(False, help="Remove cache"),
):
    """Build a project `venv`, `completions`, `docs` and `clean`."""
    Project(data, rm=rm).build(version=version, quiet=quiet, rm=rm)


@project_p.command()
@_builds.command()
def builds(
        data: Annotated[
            Path,
            typer.Argument(
                help="Path/file to project or name of project",
                autocompletion=_repos_completions,
            ),
        ] = _cwd,
        quiet: bool = True,
        rm: bool = typer.Option(False, help="Remove cache"),
):
    """Build a project `venv`, `completions`, `docs` and `clean` for all versions."""
    Project(data, rm=rm).builds(quiet=quiet, rm=rm)


@project_p.command()
@_buildrequires.command()
def buildrequires(
        data: Annotated[
            Path,
            typer.Argument(
                help="Path/file to project or name of project",
                autocompletion=_repos_completions,
            ),
        ] = _cwd,
        rm: bool = typer.Option(False, help="Remove cache"),
):
    """Build requirements."""
    for item in Project(data, rm=rm).buildrequires():
        print(item)


@gh_g.command(name="current")
@_current.command(name="current")
def current_gh_g(
        data: Annotated[
            Path,  # noqa: RUF013
            typer.Argument(help="Url, path or user (to be used with name), default None for cwd."),
        ] = None,
        repo: str = typer.Option(None, help="Repo name. If not None it will use data as the owner "
                                            "if not None, otherwise $GIT."),
):
    """Current branch."""
    print(Gh(data=data, repo=repo).current())


@project_p.command("current")
def current_project_p(
        data: Annotated[
            Path,
            typer.Argument(
                help="Path/file to project or name of project",
                autocompletion=_repos_completions,
            ),
        ] = _cwd,
        rm: bool = typer.Option(False, help="Remove cache"),
):
    """Current branch."""
    print(Project(data, rm=rm).gh.current())


@gh_g.command(name="default")
def default_gh_g(
        data: Annotated[
            Path,  # noqa: RUF013
            typer.Argument(help="Url, path or user (to be used with name), default None for cwd."),
        ] = None,
        repo: str = typer.Option(None, help="Repo name. If not None it will use data as the owner "
                                            "if not None, otherwise $GIT."),
        rm: bool = typer.Option(False, help="Remove cache"),
):
    """Default branch."""
    print(GitUrl(data=data, repo=repo).default(rm=rm))


@project_p.command(name="default")
def default_project_p(
        data: Annotated[
            Path,
            typer.Argument(
                help="Path/file to project or name of project",
                autocompletion=_repos_completions,
            ),
        ] = _cwd,
        rm: bool = typer.Option(False, help="Remove cache"),
):
    """Default branch."""
    print(Project(data, rm=rm).gh.default(rm=rm))


@project_p.command()
@_clean.command()
def clean(
        data: Annotated[
            Path,
            typer.Argument(
                help="Path/file to project or name of project",
                autocompletion=_repos_completions,
            ),
        ] = _cwd,
        rm: bool = typer.Option(False, help="Remove cache"),
):
    """Clean project."""
    Project(data, rm=rm).clean()


@gh_g.command(name="commit")
def commit_gh_g(
        data: Annotated[
            Path,  # noqa: RUF013
            typer.Argument(help="Url, path or user (to be used with name), default None for cwd."),
        ] = None,
        repo: str = typer.Option(None, help="Repo name. If not None it will use data as the owner "
                                            "if not None, otherwise $GIT."),
        msg: str = typer.Option("", "-m", "--message", "--msg", help="Commit message"),
        quiet: bool = True,
        force: bool = typer.Option(False, help="Force commit if diverged"),
):
    """Commit a project from path or name."""
    Gh(data=data, repo=repo).commit(msg if msg else None, force=force, quiet=quiet)


@project_p.command()
@_commit.command()
def commit(
        data: Annotated[
            Path,
            typer.Argument(
                help="Path/file to project or name of project",
                autocompletion=_repos_completions,
            ),
        ] = _cwd,
        msg: str = typer.Option("", "-m", "--message", "--msg", help="Commit message"),
        force: bool = typer.Option(False, help="Force commit if diverged"),
        quiet: bool = True,
):
    """Commit a project from path or name."""
    Project(data).gh.commit(msg if msg else None, force=force, quiet=quiet)


@project_p.command()
@_completions.command()
def completions(
        data: Annotated[
            Path,
            typer.Argument(
                help="Path/file to project or name of project",
                autocompletion=_repos_completions,
            ),
        ] = _cwd,
        rm: bool = typer.Option(False, help="Remove cache"),
):
    """Generate completions to /usr/local/etc/bash_completion.d."""
    Project(data, rm=rm).completions()


@project_p.command()
def coverage(
        data: Annotated[
            Path,
            typer.Argument(
                help="Path/file to project or name of project",
                autocompletion=_repos_completions,
            ),
        ] = _cwd,
        rm: bool = typer.Option(False, help="Remove cache"),
):
    """Project coverage."""
    Project(data, rm=rm).coverage()


@project_p.command()
@_dependencies.command()
def dependencies(
        data: Annotated[
            Path,
            typer.Argument(
                help="Path/file to project or name of project",
                autocompletion=_repos_completions,
            ),
        ] = _cwd,
        rm: bool = typer.Option(False, help="Remove cache"),
):
    """Project dependencies from path or name."""
    for item in Project(data, rm=rm).dependencies():
        print(item)


@gh_g.command(name="dirty")
def dirty_gh_g(
        data: Annotated[
            Path,  # noqa: RUF013
            typer.Argument(help="Url, path or user (to be used with name), default None for cwd."),
        ] = None,
        repo: str = typer.Option(None, help="Repo name. If not None it will use data as the owner "
                                            "if not None, otherwise $GIT."),
        quiet: bool = True,
):
    """Is the repo dirty?: 0 if dirty."""
    if Gh(data=data, repo=repo).status(quiet=quiet).dirty:
        sys.exit(0)
    else:
        sys.exit(1)


@project_p.command()
@_dirty.command()
def dirty(
        data: Annotated[
            Path,
            typer.Argument(
                help="Path/file to project or name of project",
                autocompletion=_repos_completions,
            ),
        ] = _cwd,
        quiet: bool = True,
):
    """Is the repo dirty?: 0 if dirty."""
    if Project(data).gh.status(quiet=quiet).dirty:
        sys.exit(0)
    else:
        sys.exit(1)


@project_p.command()
@_distribution.command()
def distribution(
        data: Annotated[
            Path,
            typer.Argument(
                help="Path/file to project or name of project",
                autocompletion=_repos_completions,
            ),
        ] = _cwd,
        rm: bool = typer.Option(False, help="Remove cache"),
):
    """Clean project."""
    print(Project(data, rm=rm).distribution())


@gh_g.command(name="diverge")
def diverge_gh_g(
        data: Annotated[
            Path,  # noqa: RUF013
            typer.Argument(help="Url, path or user (to be used with name), default None for cwd."),
        ] = None,
        repo: str = typer.Option(None, help="Repo name. If not None it will use data as the owner "
                                            "if not None, otherwise $GIT."),
        quiet: bool = True,
):
    """Does the repo diverge, dirty or need push and needpull?: 0: if diverge."""
    if Gh(data=data, repo=repo).status(quiet=quiet).diverge:
        sys.exit(0)
    else:
        sys.exit(1)


@project_p.command()
@_diverge.command()
def diverge(
        data: Annotated[
            Path,
            typer.Argument(
                help="Path/file to project or name of project",
                autocompletion=_repos_completions,
            ),
        ] = _cwd,
        quiet: bool = True,
):
    """Does the repo diverge, dirty or need push and needpull?: 0: if diverge."""
    if Project(data).gh.status(quiet=quiet).diverge:
        sys.exit(0)
    else:
        sys.exit(1)


@project_p.command()
def docker(
        data: Annotated[
            Path,
            typer.Argument(
                help="Path/file to project or name of project",
                autocompletion=_repos_completions,
            ),
        ] = _cwd,
        quiet: bool = True,
        rm: bool = typer.Option(False, help="Remove cache"),
):
    """Build and push to docker hub for python versions, latest will be PYTHON_DEFAULT_VERSION."""
    Project(data, rm=rm).docker(quiet=quiet)


@project_p.command()
@_docs.command()
def docs(
        data: Annotated[
            Path,
            typer.Argument(
                help="Path/file to project or name of project",
                autocompletion=_repos_completions,
            ),
        ] = _cwd,
        version: Annotated[str, typer.Option(help="python major and minor version",
                                             autocompletion=_versions_completions)] = PYTHON_DEFAULT_VERSION,
        quiet: bool = True,
        rm: bool = typer.Option(False, help="Remove cache"),
):
    """Build the documentation."""
    Project(data, rm=rm).docs(version=version, quiet=quiet)


@project_p.command()
def executable(
        data: Annotated[
            Path,
            typer.Argument(
                help="Path/file to project or name of project",
                autocompletion=_repos_completions,
            ),
        ] = _cwd,
        version: Annotated[str, typer.Option(help="python major and minor version",
                                             autocompletion=_versions_completions)] = PYTHON_DEFAULT_VERSION,
        rm: bool = typer.Option(False, help="Remove cache"),
):
    """Shows executable being used."""
    print(Project(data, rm=rm).executable(version=version))


@project_p.command()
@_extras.command()
def extras(
        data: Annotated[
            Path,
            typer.Argument(
                help="Path/file to project or name of project",
                autocompletion=_repos_completions,
            ),
        ] = _cwd,
        rm: bool = typer.Option(False, help="Remove cache"),
):
    """Project extras."""
    for item in Project(data, rm=rm).extras(as_list=True):
        print(item)


@gh_g.command(name="github")
def github_gh_g(
        data: Annotated[
            Path,  # noqa: RUF013
            typer.Argument(help="Url, path or user (to be used with name), default None for cwd."),
        ] = None,
        repo: str = typer.Option(None, help="Repo name. If not None it will use data as the owner "
                                            "if not None, otherwise $GIT."),
        rm: bool = typer.Option(False, help="Remove cache"),
):
    """GitHub repos API."""
    from rich import print_json
    print_json(data=GitUrl(data=data, repo=repo).github(rm=rm))


@project_p.command(name="github")
def github_project_p(
        data: Annotated[
            Path,
            typer.Argument(
                help="Path/file to project or name of project",
                autocompletion=_repos_completions,
            ),
        ] = _cwd,
        rm: bool = typer.Option(False, help="Remove cache"),
):
    """GitHub repos API."""
    from rich import print_json
    print_json(data=Project(data, rm=rm).gh.github(rm=rm))


@_ipy.command()
def __ipy():
    """Run IPython."""
    ipy()


@project_p.command()
@_ipythondir.command()
def ipythondir():
    """IPython Profile :mod:`ipython_profile.profile_default.ipython_config`: `export IPYTHONDIR="$(ipythondir)"`."""
    print(IPYTHONDIR)


@gh_g.command(name="latest")
def latest_gh_g(
        data: Annotated[
            Path,  # noqa: RUF013
            typer.Argument(help="Url, path or user (to be used with name), default None for cwd."),
        ] = None,
        repo: str = typer.Option(None, help="Repo name. If not None it will use data as the owner "
                                            "if not None, otherwise $GIT."),
):
    """Latest tag."""
    print(Gh(data=data, repo=repo).latest())


@project_p.command()
@_latest.command()
def latest(
        data: Annotated[
            Path,
            typer.Argument(
                help="Path/file to project or name of project",
                autocompletion=_repos_completions,
            ),
        ] = _cwd,
):
    """Latest tag."""
    print(Project(data).gh.latest())


@project_p.command(name="mip")
@_mip.command(name="mip")
def __mip():
    """Public IP."""
    print(mip())


@gh_g.command(name="needpull")
def needpull_gh_g(
        data: Annotated[
            Path,  # noqa: RUF013
            typer.Argument(help="Url, path or user (to be used with name), default None for cwd."),
        ] = None,
        repo: str = typer.Option(None, help="Repo name. If not None it will use data as the owner "
                                            "if not None, otherwise $GIT."),
        quiet: bool = True,
):
    """Does the repo need to be pulled?: 0 if needs pull."""
    if Gh(data=data, repo=repo).status(quiet=quiet).pull:
        sys.exit(0)
    else:
        sys.exit(1)


@project_p.command()
@_needpull.command()
def needpull(
        data: Annotated[
            Path,
            typer.Argument(
                help="Path/file to project or name of project",
                autocompletion=_repos_completions,
            ),
        ] = _cwd,
        quiet: bool = True,
):
    """Does the repo need to be pulled?: 0 if needs pull."""
    if Project(data).gh.status(quiet=quiet).pull:
        sys.exit(0)
    else:
        sys.exit(1)


@gh_g.command(name="needpush")
def needpush_gh_g(
        data: Annotated[
            Path,  # noqa: RUF013
            typer.Argument(help="Url, path or user (to be used with name), default None for cwd."),
        ] = None,
        repo: str = typer.Option(None, help="Repo name. If not None it will use data as the owner "
                                            "if not None, otherwise $GIT."),
        quiet: bool = True,
):
    """Does the repo need to be pushed?: 0 if needs push."""
    if Gh(data=data, repo=repo).status(quiet=quiet).push:
        sys.exit(0)
    else:
        sys.exit(1)


@project_p.command()
@_needpush.command()
def needpush(
        data: Annotated[
            Path,
            typer.Argument(
                help="Path/file to project or name of project",
                autocompletion=_repos_completions,
            ),
        ] = _cwd,
        quiet: bool = True,
):
    """Does the repo need to be pushed?: 0 if needs push."""
    if Project(data).gh.status(quiet=quiet).push:
        sys.exit(0)
    else:
        sys.exit(1)


@gh_g.command(name="next")
def next_gh_g(
        data: Annotated[
            Path,  # noqa: RUF013
            typer.Argument(help="Url, path or user (to be used with name), default None for cwd."),
        ] = None,
        repo: str = typer.Option(None, help="Repo name. If not None it will use data as the owner "
                                            "if not None, otherwise $GIT."),
        part: Annotated[Bump, typer.Option(help="part to increase if force")] = Bump.PATCH,
        force: Annotated[bool, typer.Option(help="force bump")] = False,
):
    """Show next version based on fix: feat: or BREAKING CHANGE:."""
    print(Gh(data=data, repo=repo).next(part=part, force=force))


@project_p.command(name="next")
@_next.command(name="next")
def __next(
        data: Annotated[
            Path,
            typer.Argument(
                help="Path/file to project or name of project",
                autocompletion=_repos_completions,
            ),
        ] = _cwd,
        part: Annotated[Bump, typer.Option(help="part to increase if force")] = Bump.PATCH,
        force: Annotated[bool, typer.Option(help="force bump")] = False,
):
    """Show next version based on fix: feat: or BREAKING CHANGE:."""
    print(Project(data=data).gh.next(part=part, force=force))


@gh_g.command(name="public")
def public_gh_g(
        data: Annotated[
            Path,  # noqa: RUF013
            typer.Argument(help="Url, path or user (to be used with name), default None for cwd."),
        ] = None,
        repo: str = typer.Option(None, help="Repo name. If not None it will use data as the owner "
                                            "if not None, otherwise $GIT."),
        rm: bool = typer.Option(False, help="Remove cache"),
):
    """Is repository public?."""
    sys.exit(int(not GitUrl(data=data, repo=repo).public(rm=rm)))


@project_p.command(name="public")
def public_project_p(
        data: Annotated[
            Path,
            typer.Argument(
                help="Path/file to project or name of project",
                autocompletion=_repos_completions,
            ),
        ] = _cwd,
        rm: bool = typer.Option(False, help="Remove cache"),
):
    """Is repository public?"""
    sys.exit(int(not Project(data, rm=rm).gh.public(rm=rm)))


@project_p.command()
@_publish.command()
def publish(
        data: Annotated[
            Path,
            typer.Argument(
                help="Path/file to project or name of project",
                autocompletion=_repos_completions,
            ),
        ] = _cwd,
        part: Annotated[Bump, typer.Option(help="part to increase if force")] = Bump.PATCH,
        force: Annotated[bool, typer.Option(help="force bump")] = False,
        ruff: Annotated[bool, typer.Option(help="run ruff")] = True,
        tox: Annotated[bool, typer.Option(help="run tox")] = False,
        quiet: bool = True,
        rm: bool = typer.Option(False, help="Remove cache"),
):
    """Publish runs runs `tests`, `commit`, `tag`, `push`, `twine` and `clean`."""
    Project(data, rm=rm).publish(part=part, force=force, ruff=ruff, tox=tox, quiet=quiet, rm=rm)


@gh_g.command(name="pull")
def pull_gh_g(
        data: Annotated[
            Path,  # noqa: RUF013
            typer.Argument(help="Url, path or user (to be used with name), default None for cwd."),
        ] = None,
        repo: str = typer.Option(None, help="Repo name. If not None it will use data as the owner "
                                            "if not None, otherwise $GIT."),
        force: bool = typer.Option(False, help="Force commit if diverged"),
        quiet: bool = True,
):
    """Pull repo."""
    Gh(data=data, repo=repo).pull(force=force, quiet=quiet)


@project_p.command()
@_pull.command()
def pull(
        data: Annotated[
            Path,
            typer.Argument(
                help="Path/file to project or name of project",
                autocompletion=_repos_completions,
            ),
        ] = _cwd,
        force: bool = typer.Option(False, help="Force commit if diverged"),
        quiet: bool = True,
):
    """Pull repo."""
    Project(data).gh.pull(force=force, quiet=quiet)


@gh_g.command(name="push")
def push_gh_g(
        data: Annotated[
            Path,  # noqa: RUF013
            typer.Argument(help="Url, path or user (to be used with name), default None for cwd."),
        ] = None,
        repo: str = typer.Option(None, help="Repo name. If not None it will use data as the owner "
                                            "if not None, otherwise $GIT."),
        force: bool = typer.Option(False, help="Force push"),
        quiet: bool = True,
):
    """Push repo."""
    Gh(data=data, repo=repo).push(force=force, quiet=quiet)


@project_p.command()
@_push.command()
def push(
        data: Annotated[
            Path,
            typer.Argument(
                help="Path/file to project or name of project",
                autocompletion=_repos_completions,
            ),
        ] = _cwd,
        force: bool = typer.Option(False, help="Force push"),
        quiet: bool = True,
):
    """Push repo."""
    Project(data).gh.push(force=force, quiet=quiet)


@project_p.command()
@_pypi.command()
def pypi(
        data: Annotated[
            Path,
            typer.Argument(
                help="Path/file to project or name of project",
                autocompletion=_repos_completions,
            ),
        ] = _cwd,
        rm: bool = typer.Option(False, help="Remove cache"),
):
    """Pypi information for a package."""
    print(Project(data, rm=rm).pypi(rm=rm))


@project_p.command()
def pytest(
        data: Annotated[
            Path,
            typer.Argument(
                help="Path/file to project or name of project",
                autocompletion=_repos_completions,
            ),
        ] = _cwd,
        version: Annotated[str, typer.Option(help="python major and minor version",
                                             autocompletion=_versions_completions)] = PYTHON_DEFAULT_VERSION,
        rm: bool = typer.Option(False, help="Remove cache"),
):
    """Run pytest."""
    sys.exit(Project(data, rm=rm).pytest(version=version))


@project_p.command()
@_pytests.command()
def pytests(
        data: Annotated[
            Path,
            typer.Argument(
                help="Path/file to project or name of project",
                autocompletion=_repos_completions,
            ),
        ] = _cwd,
        rm: bool = typer.Option(False, help="Remove cache"),
):
    """Run pytest for all versions."""
    sys.exit(Project(data, rm=rm).pytests())


@project_p.command()
@_pythonstartup.command()
def pythonstartup():
    """Python Startup :mod:`python_startup.__init__`: `export PYTHONSTARTUP="$(pythonstartup)"`."""
    print(PYTHONSTARTUP)


@gh_g.command(name="remote")
def remote_gh_g(
        data: Annotated[
            Path,  # noqa: RUF013
            typer.Argument(help="Url, path or user (to be used with name), default None for cwd."),
        ] = None,
        repo: str = typer.Option(None, help="Repo name. If not None it will use data as the owner "
                                            "if not None, otherwise $GIT."),
):
    """Remote url."""
    print(Gh(data=data, repo=repo).url)


@project_p.command()
@_remote.command()
def remote(
        data: Annotated[
            Path,
            typer.Argument(
                help="Path/file to project or name of project",
                autocompletion=_repos_completions,
            ),
        ] = _cwd,
):
    """Remote url."""
    print(Project(data).gh.url)


@project_p.command()
@_repos.command()
def repos(
        data: Annotated[
            Path,
            typer.Argument(
                help="Path/file to project or name of project",
                autocompletion=_repos_completions,
            ),
        ] = _cwd,
        ret: Annotated[ProjectRepos, typer.Option(help="return names, paths, dict or instances")] = ProjectRepos.NAMES,
        sync: Annotated[bool, typer.Option(help="push or pull all repos")] = False,
        archive: Annotated[bool, typer.Option(help="look for repos under ~/Archive")] = False,
        rm: bool = typer.Option(False, help="Remove cache"),
):
    """Manage repos and projects under HOME and HOME/Archive."""
    rv = Project(data, rm=rm).repos(ret=ret, sync=sync, archive=archive, rm=rm)
    if sync is False:
        if ret == ProjectRepos.PATHS:
            for repo in rv:
                print(str(repo))
        else:
            for repo in rv:
                print(repo)


@project_p.command()
@_requirement.command()
def requirement(
        data: Annotated[
            Path,
            typer.Argument(
                help="Path/file to project or name of project",
                autocompletion=_repos_completions,
            ),
        ] = _cwd,
        version: Annotated[str, typer.Option(help="python major and minor version",
                                             autocompletion=_versions_completions)] = PYTHON_DEFAULT_VERSION,
        install: Annotated[bool, typer.Option(help="install requirements, dependencies and extras")] = False,
        upgrade: Annotated[bool, typer.Option(help="upgrade requirements, dependencies and extras")] = False,
        quiet: bool = True,
        rm: bool = typer.Option(False, help="Remove cache"),
):
    """Requirements for package."""
    rv = Project(data, rm=rm).requirement(version=version, install=install, upgrade=upgrade, quiet=quiet)
    if install or upgrade:
        return
    for item in rv:
        print(item)


@project_p.command()
@_requirements.command()
def requirements(
        data: Annotated[
            Path,
            typer.Argument(
                help="Path/file to project or name of project",
                autocompletion=_repos_completions,
            ),
        ] = _cwd,
        upgrade: Annotated[bool, typer.Option(help="upgrade requirements, dependencies and extras")] = False,
        quiet: bool = True,
        rm: bool = typer.Option(False, help="Remove cache"),
):
    """Install requirements for all python versions."""
    Project(data, rm=rm).requirements(upgrade=upgrade, quiet=quiet)


@project_p.command(name="ruff")
def _ruff(
        data: Annotated[
            Path,
            typer.Argument(
                help="Path/file to project or name of project",
                autocompletion=_repos_completions,
            ),
        ] = _cwd,
        version: Annotated[str, typer.Option(help="python major and minor version",
                                             autocompletion=_versions_completions)] = PYTHON_DEFAULT_VERSION,
):
    """Run ruff."""
    sys.exit(Project(data).ruff(version=version))


@gh_g.command(name="secrets")
def secrets_gh_g(
        data: Annotated[
            Path,  # noqa: RUF013
            typer.Argument(help="Url, path or user (to be used with name), default None for cwd."),
        ] = None,
        repo: str = typer.Option(None, help="Repo name. If not None it will use data as the owner "
                                            "if not None, otherwise $GIT."),
        force: bool = typer.Option(False, help="For update secrets, otherwise update if empty."),
):
    """Update GitHub repository secrets."""
    Gh(data=data, repo=repo).secrets(force=force)


@project_p.command()
@_secrets.command()
def secrets(
        data: Annotated[
            Path,
            typer.Argument(
                help="Path/file to project or name of project",
                autocompletion=_repos_completions,
            ),
        ] = _cwd,
        force: bool = typer.Option(False, help="For update secrets, otherwise update if empty."),
):
    """Update GitHub repository secrets."""
    Project(data).gh.secrets(force=force)


@gh_g.command(name="secrets-names")
def secrets_names_gh_g(
        data: Annotated[
            Path,  # noqa: RUF013
            typer.Argument(help="Url, path or user (to be used with name), default None for cwd."),
        ] = None,
        repo: str = typer.Option(None, help="Repo name. If not None it will use data as the owner "
                                            "if not None, otherwise $GIT."),
):
    """List GitHub repository secrets names."""
    for item in Gh(data=data, repo=repo).secrets_names():
        print(item)


@project_p.command(name="secrets-names")
@_secrets_names.command(name="secrets-names")
def secrets_names(
        data: Annotated[
            Path,
            typer.Argument(
                help="Path/file to project or name of project",
                autocompletion=_repos_completions,
            ),
        ] = _cwd,
):
    """List GitHub repository secrets names."""
    for item in Project(data).gh.secrets_names():
        print(item)


@gh_g.command(name="status")
def status_git_g(
        data: Annotated[
            Path,  # noqa: RUF013
            typer.Argument(help="Url, path or user (to be used with name), default None for cwd."),
        ] = None,
        repo: str = typer.Option(None, help="Repo name. If not None it will use data as the owner "
                                            "if not None, otherwise $GIT."),
        quiet: bool = True,
):
    """Git status for a project."""
    from rich import print_json
    print_json(data=dataclasses.asdict(Gh(data=data, repo=repo).status(quiet=quiet)))


@project_p.command()
@_status.command()
def status(
        data: Annotated[
            Path,
            typer.Argument(
                help="Path/file to project or name of project",
                autocompletion=_repos_completions,
            ),
        ] = _cwd,
        quiet: bool = True,
):
    """Git status for a project."""
    from rich import print_json
    print_json(data=dataclasses.asdict(Project(data).gh.status(quiet=quiet)))


@gh_g.command(name="superproject")
def superproject_gh_g(
        data: Annotated[
            Path,  # noqa: RUF013
            typer.Argument(help="Url, path or user (to be used with name), default None for cwd.", ),
        ] = None,
        repo: str = typer.Option(None, help="Repo name. If not None it will use data as the owner"),
):
    """Superproject path."""
    print(Gh(data=data, repo=repo).superproject())


@project_p.command()
@_superproject.command()
def superproject(
        data: Annotated[
            Path,
            typer.Argument(
                help="Path/file to project or name of project",
                autocompletion=_repos_completions,
            ),
        ] = _cwd,
):
    """Superproject path."""
    print(Project(data).gh.superproject())


@gh_g.command(name="sync")
def sync_gh_g(
        data: Annotated[
            Path,  # noqa: RUF013
            typer.Argument(help="Url, path or user (to be used with name), default None for cwd."),
        ] = None,
        repo: str = typer.Option(None, help="Repo name. If not None it will use data as the owner "
                                            "if not None, otherwise $GIT."),
):
    """Sync repo."""
    Gh(data=data, repo=repo).sync()


@project_p.command(name="sync")
def __sync(
        data: Annotated[
            Path,
            typer.Argument(
                help="Path/file to project or name of project",
                autocompletion=_repos_completions,
            ),
        ] = _cwd,
        rm: bool = typer.Option(False, help="Remove cache"),
):
    """Sync repo."""
    Project(data, rm=rm).gh.sync()


@gh_g.command(name="tag")
def tag_gh_g(
        tag: str,
        data: Annotated[
            Path,  # noqa: RUF013
            typer.Argument(help="Url, path or user (to be used with name), default None for cwd."),
        ] = None,
        repo: str = typer.Option(None, help="Repo name. If not None it will use data as the owner "
                                            "if not None, otherwise $GIT."),
        quiet: bool = True,
):
    """Latest tag."""
    print(Gh(data=data, repo=repo).tag(tag=tag, quiet=quiet))


@project_p.command("tag")
def __tag(
        tag: str,
        data: Annotated[
            Path,
            typer.Argument(
                help="Path/file to project or name of project",
                autocompletion=_repos_completions,
            ),
        ] = _cwd,
        quiet: bool = True,
):
    """Tag repo."""
    Project(data).gh.tag(tag=tag, quiet=quiet)


@project_p.command(name="test")
def test(
        data: Annotated[
            Path,
            typer.Argument(
                help="Path/file to project or name of project",
                autocompletion=_repos_completions,
            ),
        ] = _cwd,
        version: Annotated[str, typer.Option(help="python major and minor version",
                                             autocompletion=_versions_completions)] = PYTHON_DEFAULT_VERSION,
        ruff: Annotated[bool, typer.Option(help="run ruff")] = True,
        tox: Annotated[bool, typer.Option(help="run tox")] = False,
        quiet: bool = True,
        rm: bool = typer.Option(False, help="Remove cache"),
):
    """Test project, runs `build`, `ruff`, `pytest` and `tox`."""
    sys.exit(Project(data, rm=rm).test(version=version, ruff=ruff, tox=tox, quiet=quiet))


@project_p.command(name="tests")
@_tests.command(name="tests")
def tests(
        data: Annotated[
            Path,
            typer.Argument(
                help="Path/file to project or name of project",
                autocompletion=_repos_completions,
            ),
        ] = _cwd,
        ruff: Annotated[bool, typer.Option(help="run ruff")] = True,
        tox: Annotated[bool, typer.Option(help="run tox")] = False,
        quiet: bool = True,
        rm: bool = typer.Option(False, help="Remove cache"),
):
    """Test project, runs `build`, `ruff`, `pytest` and `tox`."""
    sys.exit(Project(data, rm=rm).tests(ruff=ruff, tox=tox, quiet=quiet))


@gh_g.command(name="top")
def top_gh_g(
        data: Annotated[
            Path,  # noqa: RUF013
            typer.Argument(help="Url, path or user (to be used with name), default None for cwd.", ),
        ] = None,
        repo: str = typer.Option(None, help="Repo name. If not None it will use data as the owner"),
):
    """Top path."""
    print(Gh(data=data, repo=repo).top())


@project_p.command()
def top(
        data: Annotated[
            Path,
            typer.Argument(
                help="Path/file to project or name of project",
                autocompletion=_repos_completions,
            ),
        ] = _cwd,
):
    """Top path."""
    print(Project(data).gh.top())


@project_p.command(name="tox")
def _tox(
        data: Annotated[
            Path,
            typer.Argument(
                help="Path/file to project or name of project",
                autocompletion=_repos_completions,
            ),
        ] = _cwd,
):
    """Run tox."""
    sys.exit(Project(data).tox())


@project_p.command()
def twine(
        data: Annotated[
            Path,
            typer.Argument(
                help="Path/file to project or name of project",
                autocompletion=_repos_completions,
            ),
        ] = _cwd,
        part: Annotated[Bump, typer.Option(help="part to increase if force")] = Bump.PATCH,
        force: Annotated[bool, typer.Option(help="force bump")] = False,
        rm: bool = typer.Option(False, help="Remove cache"),
):
    """Run twine."""
    sys.exit(Project(data, rm=rm).twine(part=part, force=force, rm=rm))


@project_p.command(name="version")
@_version.command(name="version")
def __version(
        data: Annotated[
            Path,
            typer.Argument(
                help="Path/file to project or name of project",
                autocompletion=_repos_completions,
            ),
        ] = _cwd,
        rm: bool = typer.Option(True, help="Remove cache"),
):
    """Project version from pyproject.toml, tag, distribution or pypi."""
    print(Project(data, rm=rm).version(rm=rm))


@project_p.command()
@_venv.command()
def venv(
        data: Annotated[
            Path,
            typer.Argument(
                help="Path/file to project or name of project",
                autocompletion=_repos_completions,
            ),
        ] = _cwd,
        version: Annotated[str, typer.Option(help="python major and minor version",
                                             autocompletion=_versions_completions)] = PYTHON_DEFAULT_VERSION,
        clear: Annotated[bool, typer.Option(help="force removal of venv before")] = False,
        upgrade: Annotated[bool, typer.Option(help="upgrade all dependencies")] = False,
        quiet: bool = True,
        rm: bool = typer.Option(False, help="Remove cache"),
):
    """Creates venv, runs: `write` and `requirements`."""
    Project(data, rm=rm).venv(version=version, clear=clear, upgrade=upgrade, quiet=quiet, rm=rm)


@project_p.command()
@_venvs.command()
def venvs(
        data: Annotated[
            Path,
            typer.Argument(
                help="Path/file to project or name of project",
                autocompletion=_repos_completions,
            ),
        ] = _cwd,
        upgrade: Annotated[bool, typer.Option(help="upgrade all dependencies")] = False,
        quiet: bool = True,
        rm: bool = typer.Option(False, help="Remove cache"),
):
    """Creates venv, runs: `write` and `requirements`."""
    Project(data, rm=rm).venvs(upgrade=upgrade, quiet=quiet, rm=rm)


@project_p.command()
def write(
        data: Annotated[
            Path,
            typer.Argument(
                help="Path/file to project or name of project",
                autocompletion=_repos_completions,
            ),
        ] = _cwd,
        rm: bool = typer.Option(False, help="Remove cache"),
):
    """Updates pyproject.toml and docs conf.py."""
    Project(data, rm=rm).write(rm=rm)


if "sphinx" in sys.modules and __name__ != "__main__":
    with pipmetapathfinder():
        import tomlkit

    text = """# Usage

```{eval-rst}
"""
    root = Path(__file__).parent.parent.parent
    pyproject_toml = root / "pyproject.toml"
    file = root / "docs/usage.md"
    if file.exists():
        original = file.read_text()
        with Path.open(pyproject_toml, "rb") as f:
            toml = tomlkit.load(f)

            new = copy.deepcopy(toml)
            new["project"]["scripts"] = {}
        for key, value in globals().copy().items():
            if isinstance(value, typer.Typer):
                cls = f"{NODEPS_PROJECT_NAME}.__main__:{key}"
                new["project"]["scripts"][value.info.name] = cls
                text += f".. click:: {cls}_click\n"
                text += f"    :prog: {value.info.name}\n"
                text += "    :nested: full\n\n"
                globals()[f"{key}_click"] = typer.main.get_command(value)
        text += "```\n"
        if original != text:
            file.write_text(text)
            print(f"{file}: updated!")
        new["project"] = dict_sort(new["project"])
        if toml != new:
            with pyproject_toml.open("w") as f:
                tomlkit.dump(new, f)
                print(f"{pyproject_toml}: updated!")

# https://github.com/tiangolo/typer/issues/498
typer.completion.completion_init()

if __name__ == "__main__":
    try:
        sys.exit(project_p())
    except KeyboardInterrupt:
        print("Aborted!")
        sys.exit(1)
