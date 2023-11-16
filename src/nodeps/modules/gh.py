"""GH Module."""
__all__ = (
    "GIT_CONFIG_GLOBAL",
    "GitUrl",
    "Gh",
    "aioclone",
    "clone",
    "git_config_global",
)

import collections
import dataclasses
import os
import subprocess
import tempfile
import urllib.error
from typing import ClassVar, Protocol, cast, runtime_checkable

from nodeps.modules.classes import ColorLogger
from nodeps.modules.constants import CI, DOCKER, EMAIL, GIT, GITHUB_TOKEN, GITHUB_URL, NODEPS_PROJECT_NAME
from nodeps.modules.datas import GitStatus
from nodeps.modules.enums import Bump
from nodeps.modules.errors import InvalidArgumentError
from nodeps.modules.functions import aiocmd, cmd, stdout, urljson
from nodeps.modules.path import Path
from nodeps.modules.platforms import (
    PLATFORMS,
    AssemblaPlatform,
    BasePlatform,
    BitbucketPlatform,
    FriendCodePlatform,
    GitHubPlatform,
    GitLabPlatform,
)

GIT_CONFIG_GLOBAL = {
    "init.defaultBranch": "main",
    "pull.rebase": "false",
    "user.email": EMAIL,
    "user.name": GIT,
}


@runtime_checkable
class _SupportsWorkingDir(Protocol):
    """Protocol Class to support Repo class."""

    @property
    def working_dir(self):
        return


@dataclasses.dataclass
class GitUrl:
    """Parsed Git URL Helper Class.

    Attributes:
        data: Url, path or user (to be used with name), default None for cwd. Does not have .git unless is git+file
        repo: Repo name. If not None it will use data as the owner if not None, otherwise $GIT.

    Examples:
            >>> import nodeps
            >>> from nodeps import GitUrl
            >>> from nodeps import Path
            >>> from nodeps import NODEPS_PROJECT_NAME, CI
            >>> from nodeps import NODEPS_PATH
            >>>
            >>> p = GitUrl()
            >>> p1 = GitUrl(nodeps.__file__)
            >>> p2 = GitUrl(repo=NODEPS_PROJECT_NAME)
            >>> p.host, p.owner, p.repo, p.protocol, p.protocols, p.platform, p.pathname, p.ownerrepo
            ('github.com', 'j5pu', 'nodeps', 'https', ['https'], 'github', '/j5pu/nodeps', 'j5pu/nodeps')
            >>> assert p2.url == p1.url == p.url == "https://github.com/j5pu/nodeps"
            >>> if not CI:
            ...     assert NODEPS_PATH == p1._path
            >>>
            >>> u = 'git@bitbucket.org:AaronO/some-repo.git'
            >>> p = GitUrl(u)
            >>> p.host, p.owner, p.repo, p.protocol, p.protocols, p.platform, p.pathname, p.ownerrepo
            ('bitbucket.org', 'AaronO', 'some-repo', 'ssh', ['ssh'], 'bitbucket', 'AaronO/some-repo.git',\
 'AaronO/some-repo')
            >>> assert p.normalized == u
            >>> assert p.url == u.removesuffix(".git")
            >>> assert p.ownerrepo == "AaronO/some-repo"
            >>>
            >>> u = "https://github.com/cpython/cpython"
            >>> p = GitUrl(u)
            >>> p.host, p.owner, p.repo, p.protocol, p.protocols, p.platform, p.pathname, p.ownerrepo
            ('github.com', 'cpython', 'cpython', 'https', ['https'], 'github', '/cpython/cpython', 'cpython/cpython')
            >>> assert p.normalized == u + ".git"
            >>> assert p.url == u
            >>>
            >>> p1 = GitUrl(data="cpython", repo="cpython")
            >>> assert p == p1
            >>>
            >>> u = "git+https://github.com/cpython/cpython"
            >>> p = GitUrl(u)
            >>> p.host, p.owner, p.repo, p.protocol, p.protocols, p.platform, p.pathname, p.ownerrepo
            ('github.com', 'cpython', 'cpython', 'https', ['git', 'https'], 'github', '/cpython/cpython',\
 'cpython/cpython')
            >>> p.normalized, p.url, p.url2githttps
            ('https://github.com/cpython/cpython.git', 'git+https://github.com/cpython/cpython',\
 'git+https://github.com/cpython/cpython.git')
            >>> assert p.normalized == u.removeprefix("git+") + ".git"
            >>> assert p.url == u
            >>> assert p.url2githttps == u + ".git"
            >>>
            >>> u = "git+ssh://git@github.com/cpython/cpython"
            >>> p = GitUrl(u)
            >>> p.host, p.owner, p.repo, p.protocol, p.protocols, p.platform, p.pathname, p.ownerrepo
            ('github.com', 'cpython', 'cpython', 'ssh', ['git', 'ssh'], 'github', '/cpython/cpython', 'cpython/cpython')
            >>> p.normalized, p.url, p.url2githttps
            ('git@github.com:cpython/cpython.git', 'git+ssh://git@github.com/cpython/cpython',\
 'git+https://github.com/cpython/cpython.git')
            >>> assert p.normalized == 'git@github.com:cpython/cpython.git'
            >>> assert p.url == u
            >>> assert p.url2gitssh == u + ".git"
            >>>
            >>> u = "git@github.com:cpython/cpython"
            >>> p = GitUrl(u)
            >>> p.host, p.owner, p.repo, p.protocol, p.protocols, p.platform, p.pathname, p.ownerrepo
            ('github.com', 'cpython', 'cpython', 'ssh', ['ssh'], 'github', 'cpython/cpython', 'cpython/cpython')
            >>> p.normalized, p.url, p.url2git
            ('git@github.com:cpython/cpython.git', 'git@github.com:cpython/cpython',\
 'git://github.com/cpython/cpython.git')
            >>> assert p.normalized == u + ".git"
            >>> assert p.url == u
            >>>
            >>> u = "https://domain.com/cpython/cpython"
            >>> p = GitUrl(u)
            >>> p.host, p.owner, p.repo, p.protocol, p.protocols, p.platform, p.pathname, p.ownerrepo
            ('domain.com', 'cpython', 'cpython', 'https', ['https'], 'gitlab', '/cpython/cpython', 'cpython/cpython')
            >>> p.normalized, p.url, p.url2https
            ('https://domain.com/cpython/cpython.git', 'https://domain.com/cpython/cpython',\
 'https://domain.com/cpython/cpython.git')
            >>> assert p.normalized == u + ".git"
            >>> assert p.url == u
            >>>
            >>> u = "git+https://domain.com/cpython/cpython"
            >>> p = GitUrl(u)
            >>> p.host, p.owner, p.repo, p.protocol, p.protocols, p.platform, p.pathname, p.ownerrepo
            ('domain.com', 'cpython', 'cpython', 'https', ['git', 'https'], 'gitlab', '/cpython/cpython',\
 'cpython/cpython')
            >>> p.normalized, p.url, p.url2githttps
            ('https://domain.com/cpython/cpython.git', 'git+https://domain.com/cpython/cpython',\
 'git+https://domain.com/cpython/cpython.git')
            >>> assert p.normalized == u.removeprefix("git+") + ".git"
            >>> assert p.url == u
            >>> assert p.url2githttps == u + ".git"
            >>>
            >>> u = "git+ssh://git@domain.com/cpython/cpython"
            >>> p = GitUrl(u)
            >>> p.host, p.owner, p.repo, p.protocol, p.protocols, p.platform, p.pathname, p.ownerrepo
            ('domain.com', 'cpython', 'cpython', 'ssh', ['git', 'ssh'], 'gitlab', '/cpython/cpython', 'cpython/cpython')
            >>> p.normalized, p.url, p.url2gitssh
            ('git@domain.com:cpython/cpython.git', 'git+ssh://git@domain.com/cpython/cpython',\
 'git+ssh://git@domain.com/cpython/cpython.git')
            >>> assert p.normalized == "git@domain.com:cpython/cpython.git"
            >>> assert p.url == u
            >>> assert p.url2gitssh == u + ".git"
            >>>
            >>> u = "git@domain.com:cpython/cpython"
            >>> p = GitUrl(u)
            >>> p.host, p.owner, p.repo, p.protocol, p.protocols, p.platform, p.pathname, p.ownerrepo
            ('domain.com', 'cpython', 'cpython', 'ssh', ['ssh'], 'gitlab', 'cpython/cpython', 'cpython/cpython')
            >>> p.normalized, p.url, p.url2ssh
            ('git@domain.com:cpython/cpython.git', 'git@domain.com:cpython/cpython',\
 'git@domain.com:cpython/cpython.git')
            >>> assert p.normalized == u + ".git"
            >>> assert p.url == u
            >>> assert p.url2ssh == u + ".git"
            >>>
            >>> u = "git+file:///tmp/cpython.git"
            >>> p = GitUrl(u)
            >>> p.host, p.owner, p.repo, p.protocol, p.protocols, p.platform, p.pathname, p.ownerrepo
            ('/tmp', '', 'cpython', 'file', ['git', 'file'], 'base', '/cpython.git', 'cpython')
            >>> p.normalized, p.url
            ('git+file:///tmp/cpython.git', 'git+file:///tmp/cpython.git')
            >>>
            >>> p = GitUrl("git+file:///tmp/cpython")
            >>> p.host, p.owner, p.repo, p.protocol, p.protocols, p.platform, p.pathname, p.ownerrepo
            ('/tmp', '', 'cpython', 'file', ['git', 'file'], 'base', '/cpython', 'cpython')
            >>> p.normalized, p.url
            ('git+file:///tmp/cpython.git', 'git+file:///tmp/cpython.git')
            >>> assert p.normalized == u
            >>> assert p.url == u
    """

    data: dataclasses.InitVar[str | Path | _SupportsWorkingDir | None] = ""
    """Url, path or user (to be used with name), default None for cwd. Does not have .git unless is git+file"""
    repo: str = dataclasses.field(default="", hash=True)
    """Repo name. If not None it will use data as the owner if not None, otherwise $GIT."""

    _platform_obj: (
            AssemblaPlatform | BasePlatform | BitbucketPlatform | FriendCodePlatform | GitHubPlatform | GitLabPlatform
    ) = dataclasses.field(default_factory=BasePlatform, init=False)
    _path: Path | None = dataclasses.field(default=None, init=False)
    """Path from __post_init__ method when path is provided in url argument."""
    _user: str = dataclasses.field(default="", init=False)
    access_token: str = dataclasses.field(default="", init=False)
    branch: str = dataclasses.field(default="", init=False)
    domain: str = dataclasses.field(default="", init=False)
    groups_path: str = dataclasses.field(default="", init=False)
    owner: str = dataclasses.field(default="", hash=True, init=False)
    ownerrepo: str = dataclasses.field(default="", init=False)
    path: str = dataclasses.field(default="", init=False)
    pathname: str = dataclasses.field(default="", init=False)
    path_raw: str = dataclasses.field(default="", init=False)
    platform: str = dataclasses.field(default="", init=False)
    protocol: str = dataclasses.field(default="", init=False)
    protocols: list[str] = dataclasses.field(default_factory=list, init=False)
    port: str = dataclasses.field(default="", init=False)
    url: str | Path = dataclasses.field(default="", hash=True, init=False)
    username: str = dataclasses.field(default="", init=False)
    api_repos_url: ClassVar[str] = f"{GITHUB_URL['api']}/repos"

    def __post_init__(self, data: str | Path | _SupportsWorkingDir | None):  # noqa: PLR0912, PLR0915
        """Post Init."""
        data = data.working_dir if isinstance(data, _SupportsWorkingDir) else data
        self.url = "" if data is None else str(data)  # because of CLI g default Path is None
        parsed_info = collections.defaultdict(lambda: "")
        parsed_info["protocols"] = cast(str, [])
        self._path = None

        if self.repo:
            parsed_info["repo"] = self.repo
            self.url = f"https://github.com/{self.url or GIT}/{self.repo}"
        elif not self.url:
            self._path = Path.cwd().absolute()
        elif (_path := Path(self.url)).exists():
            if _path.installed():  # GitHub Action and docker is using the installed path.
                if workspace := os.environ.get("GITHUB_WORKSPACE"):
                    self._path = Path(workspace)
                else:
                    self._path = Path.cwd().absolute()
            else:
                self._path = _path.to_parent()
        self.url = stdout(f"git -C {self._path} config --get remote.origin.url") if self._path else self.url

        if self.url is None:
            msg = f"Invalid argument: {data=}, {self.repo=}"
            raise InvalidArgumentError(msg)

        found = False
        for name, plat in PLATFORMS:
            for protocol, regex in plat.COMPILED_PATTERNS.items():
                # Match current regex against URL
                if not (match := regex.match(self.url)):
                    # Skip if not matched
                    continue

                # Skip if domain is bad
                domain = match.group("domain")

                # print('[%s] DOMAIN = %s' % (url, domain,))
                if plat.DOMAINS and domain not in plat.DOMAINS:
                    continue
                if plat.SKIP_DOMAINS and domain in plat.SKIP_DOMAINS:
                    continue

                found = True

                # add in platform defaults
                parsed_info.update(plat.DEFAULTS)

                # Get matches as dictionary
                matches = plat.clean_data(match.groupdict(default=""))

                # Update info with matches
                parsed_info.update(matches)

                owner = f"{parsed_info['owner']}/" if parsed_info["owner"] else ""

                if protocol == "ssh" and "ssh" not in parsed_info["protocols"]:
                    # noinspection PyUnresolvedReferences
                    parsed_info["protocols"].append(protocol)

                if protocol == "file" and not domain.startswith("/"):
                    msg = f"Invalid argument, git+file should have an absolute path: {data=}, {self.repo=}"
                    raise InvalidArgumentError(msg)

                parsed_info.update(
                    {
                        "url": self.url.removesuffix(".git")
                        if protocol != "file"
                        else self.url
                        if self.url.endswith(".git")
                        else f"{self.url}.git",
                        "platform": name,
                        "protocol": protocol,
                        "ownerrepo": f"{owner}{parsed_info['repo']}",
                    }
                )

                for k, v in parsed_info.items():
                    setattr(self, k, v)
                break

            if found:
                break

        for name, plat in PLATFORMS:
            if name == self.platform:
                self._platform_obj = plat
                break

        if not self.repo and self._path:
            self.repo = self._path.name

    def admin(self, user: str = GIT, rm: bool = False) -> bool:
        """Check if user has admin permissions.

        Examples:
            >>> import nodeps
            >>> from nodeps import GitUrl
            >>> from nodeps import NODEPS_PROJECT_NAME
            >>>
            >>> assert GitUrl(nodeps.__file__).admin() is True
            >>> assert GitUrl(nodeps.__file__).admin("foo") is False

        Arguments:
            user: default $GIT
            rm: use pickle cache or remove it before

        Returns:
            bool
        """
        try:
            return (
                    urljson(f"{self.api_repos_url}/{self.ownerrepo}/collaborators/{user}/permission",
                            rm=rm)["permission"]
                    == "admin"
            )
        except urllib.error.HTTPError as err:
            if err.code == 403 and err.reason == "Forbidden":  # noqa: PLR2004
                return False
            raise

    def default(self, rm: bool = False) -> str:
        """Default remote branch.

        Examples:
            >>> import nodeps
            >>> from nodeps import GitUrl
            >>>
            >>> assert GitUrl(nodeps.__file__).default() == "main"

        Args:
            rm: remove cache

        Returns:
            bool
        """
        return self.github(rm=rm)["default_branch"]

    def format(self, protocol):  # noqa: A003
        """Reformat URL to protocol."""
        items = dataclasses.asdict(self)
        items["port_slash"] = f"{self.port}/" if self.port else ""
        items["groups_slash"] = f"{self.groups_path}/" if self.groups_path else ""
        items["dot_git"] = "" if items["repo"].endswith(".git") else ".git"
        return self._platform_obj.FORMATS[protocol] % items

    def github(
            self,
            rm: bool = False,
    ) -> dict[str, str | list | dict[str, str | list | dict[str, str | list]]]:
        """GitHub repos api.

        Examples:
            >>> from nodeps import GitUrl
            >>> from nodeps import NODEPS_PROJECT_NAME
            >>>
            >>> assert GitUrl().github()["name"] == NODEPS_PROJECT_NAME

        Returns:
            dict: pypi information
            rm: use pickle cache or remove it.
        """
        return urljson(f"{self.api_repos_url}/{self.ownerrepo}", rm=rm)

    @property
    def groups(self):
        """List of groups. GitLab only."""
        if self.groups_path:
            return self.groups_path.split("/")
        return []

    @property
    def host(self):
        """Alias property for domain."""
        return self.domain

    @property
    def is_github(self):
        """GitHub platform."""
        return self.platform == "github"

    @property
    def is_bitbucket(self):
        """BitBucket platform."""
        return self.platform == "bitbucket"

    @property
    def is_friendcode(self):
        """FriendCode platform."""
        return self.platform == "friendcode"

    @property
    def is_assembla(self):
        """Assembla platform."""
        return self.platform == "assembla"

    @property
    def is_gitlab(self):
        """GitLab platform."""
        return self.platform == "gitlab"

    @property
    def name(self):
        """Alias property for repo."""
        return self.repo

    @property
    def normalized(self):
        """Normalize URL with .git."""
        return self.format(self.protocol)

    def public(self, rm: bool = False) -> bool:
        """Check if repo ius public.

        Examples:
            >>> import nodeps
            >>> from nodeps import GitUrl
            >>>
            >>> assert GitUrl(nodeps.__file__).public() is True
            >>> assert GitUrl(repo="pdf").public() is False

        Args:
            rm: remove cache

        Returns:
            bool
        """
        return self.github(rm=rm)["visibility"] == "public"

    @property
    def resource(self):
        """Alias property for domain."""
        return self.domain

    @property
    def url2git(self):
        """Rewrite url to git.

        Examples:
            >>> from nodeps import GitUrl
            >>>
            >>> url = 'git@github.com:Org/Private-repo.git'
            >>> p = GitUrl(url)
            >>> p.url2git
            'git://github.com/Org/Private-repo.git'
        """
        return self.format("git")

    @property
    def url2githttps(self):
        """Rewrite url to git.

        Examples:
            >>> from nodeps import GitUrl
            >>>
            >>> url = 'git@github.com:Org/Private-repo.git'
            >>> p = GitUrl(url)
            >>> p.url2githttps
            'git+https://github.com/Org/Private-repo.git'
        """
        return self.format("git+https")

    @property
    def url2gitssh(self):
        """Rewrite url to git.

        Examples:
            >>> from nodeps import GitUrl
            >>>
            >>> url = 'git@github.com:Org/Private-repo.git'
            >>> p = GitUrl(url)
            >>> p.url2gitssh
            'git+ssh://git@github.com/Org/Private-repo.git'
        """
        return self.format("git+ssh")

    @property
    def url2https(self):
        """Rewrite url to https.

        Examples:
            >>> from nodeps import GitUrl
            >>>
            >>> url = 'git@github.com:Org/Private-repo.git'
            >>> p = GitUrl(url)
            >>> p.url2https
            'https://github.com/Org/Private-repo.git'
        """
        return self.format("https")

    @property
    def url2ssh(self):
        """Rewrite url to ssh.

        Examples:
            >>> from nodeps import GitUrl
            >>>
            >>> url = 'git@github.com:Org/Private-repo.git'
            >>> p = GitUrl(url)
            >>> p.url2ssh
            'git@github.com:Org/Private-repo.git'
        """
        return self.format("ssh")

    @property
    def urls(self):
        """All supported urls for a repo.

        Examples:
            >>> from nodeps import GitUrl
            >>> url = 'git@github.com:Org/Private-repo.git'
            >>>
            >>> GitUrl(url).urls
            {'git': 'git://github.com/Org/Private-repo.git',\
 'git+https': 'git+https://github.com/Org/Private-repo.git',\
 'git+ssh': 'git+ssh://git@github.com/Org/Private-repo.git',\
 'https': 'https://github.com/Org/Private-repo.git',\
 'ssh': 'git@github.com:Org/Private-repo.git'}
        """
        return {protocol: self.format(protocol) for protocol in self._platform_obj.PROTOCOLS}

    @property
    def user(self):
        """Alias property for _user or owner. _user == "git for ssh."""
        if hasattr(self, "_user"):
            return self._user

        return self.owner

    @property
    def valid(self):
        """Checks if url is valid.

        It is equivalent to :meth:`validate`.

        Examples:
            >>> from nodeps import GitUrl
            >>>
            >>> url = 'git@github.com:Org/Private-repo.git'
            >>> GitUrl(url).valid
            True
            >>> GitUrl.validate(url)
            True

        """
        return all(
            [
                all(
                    getattr(self, attr, None)
                    for attr in (
                        "domain",
                        "repo",
                    )
                ),
            ]
        )

    @classmethod
    def validate(cls, data: str | Path | None = None, repo: str | None = None):
        """Validate url.

        Examples:
            >>> from nodeps import GitUrl
            >>>
            >>> u = 'git@bitbucket.org:AaronO/some-repo.git'
            >>> p = GitUrl(u)
            >>> p.host, p.owner, p.repo
            ('bitbucket.org', 'AaronO', 'some-repo')
            >>> assert p.valid is True
            >>> assert GitUrl.validate(u) is True

        Args:
            data: user (when repo is provided, default GIT), url,
                path to get from git config if exists, default None for cwd.
            repo: repo to parse url from repo and get user from data
        """
        return cls(data=data, repo=repo).valid


@dataclasses.dataclass
class Gh(GitUrl):
    """Git Repo Class.

    Examples:
        >>> import os
        >>> import pytest
        >>> import nodeps
        >>> from nodeps import Gh
        >>>
        >>> r = Gh()
        >>> r.url # doctest: +ELLIPSIS
        'https://github.com/.../nodeps'

    Args:
        owner: repo owner or Path
        repo: repo name or repo path for git+file scheme (default: None)

    Raises:
        InvalidArgumentError: if GitUrl is not initialized with path
    """

    def __post_init__(self, data: str | Path | _SupportsWorkingDir | None = None):
        """Post Init."""
        super().__post_init__(data=data)
        if not self._path:
            msg = f"Path must be provided when initializing {self.__class__.__name__}: {data=}, {self.repo=}"
            raise InvalidArgumentError(msg)

        self.git = f"git -C '{self._path}'"
        self.log = ColorLogger.logger(self.__class__.__qualname__)

        git_config_global()

    def info(self, msg: str):
        """Logger info."""
        self.log.info(msg, extra={"extra": self.repo})

    def warning(self, msg: str):
        """Logger warning."""
        self.log.warning(msg, extra={"extra": self.repo})

    def commit(self, msg: str | None = None, force: bool = False, quiet: bool = True) -> None:
        """commit.

        Raises:
            CalledProcessError: if  fails
            RuntimeError: if diverged or dirty
        """
        status = self.status(quiet=quiet)
        # print(status, file=sys.stderr)
        if status.dirty:
            if status.diverge and not force:
                msg = f"Diverged: {status=}, {self.repo=}"
                raise RuntimeError(msg)
            if msg is None or msg == "":
                msg = "fix: "
            self.git_check_call("add -A")
            self.git_check_call(f"commit -a {'--quiet' if quiet else ''} -m '{msg}'")
            self.info(self.commit.__name__)

    def config_add(self, key: str, value: str) -> None:
        """Add key and value to git repository config if not set."""
        if subprocess.run(f"{self.git} config {key}", capture_output=True, shell=True).returncode != 0:
            self.git_check_call(f"config {key} {value}")

    def current(self) -> str:
        """Current branch.

        Examples:
            >>> from nodeps import Gh
            >>>
            >>> assert Gh().current() == 'main'
        """
        return self.git_stdout("branch --show-current") or ""

    def gh_check_call(self, line: str):
        """Runs git command and raises exception if error (stdout is not captured and shown).

        Examples:
            >>> from nodeps import Gh
            >>>
            >>> assert Gh().gh_check_call("repo view") == 0  # doctest: +SKIP
        """
        return subprocess.check_call(f"gh {line}", shell=True, cwd=self._path)

    def gh_stdout(self, line: str):
        """Runs git command and returns stdout.

        Examples:
            >>> from nodeps import Gh
            >>> from nodeps import NODEPS_PROJECT_NAME
            >>>
            >>> assert NODEPS_PROJECT_NAME in Gh().gh_stdout("repo view")  # doctest: +SKIP
        """
        return stdout(f"gh {line}", cwd=self._path)

    def git_check_call(self, line: str):
        """Runs git command and raises exception if error (stdout is not captured and shown).

        Examples:
            >>> from nodeps import Gh
            >>>
            >>> assert Gh().git_check_call("rev-parse --abbrev-ref HEAD") == 0

        """
        return subprocess.check_call(f"{self.git} {line}", shell=True)

    def git_stdout(self, line: str):
        """Runs git command and returns stdout.

        Examples:
            >>> from nodeps import Gh
            >>>
            >>> assert Gh().git_stdout("rev-parse --abbrev-ref HEAD") == "main"
        """
        return stdout(f"{self.git} {line}")

    def latest(self) -> str:
        """Latest tag: git {c} describe --abbrev=0 --tags."""
        latest = self.git_stdout("tag | sort -V | tail -1") or ""
        if not latest:
            latest = "0.0.0"
            self.commit(msg=f"{self.latest.__name__}: {latest}")
            self._tag(latest)
        return latest

    def _next(self, part: Bump = Bump.PATCH) -> str:
        latest = self.latest()
        v = "v" if latest.startswith("v") else ""
        version = latest.replace(v, "").split(".")
        match part:
            case Bump.MAJOR:
                index = 0
            case Bump.MINOR:
                index = 1
            case _:
                index = 2
        version[index] = str(int(version[index]) + 1)
        return f"{v}{'.'.join(version)}"

    def next(self, part: Bump = Bump.PATCH, force: bool = False) -> str:  # noqa: A003
        """Show next version based on fix: feat: or BREAKING CHANGE:.

        Args:
            part: part to increase if force
            force: force bump
        """
        latest = self.latest()
        out = self.git_stdout(f"log --pretty=format:'%s' {latest}..@")
        if force:
            return self._next(part)
        if out:
            if "breaking change:" in out.lower():
                return self._next(Bump.MAJOR)
            if "feat:" in out.lower():
                return self._next(Bump.MINOR)
            if "fix:" in out.lower():
                return self._next()
        return latest

    def pull(self, force: bool = False, quiet: bool = True) -> None:
        """pull.

        Raises:
            CalledProcessError: if pull fails
            RuntimeError: if diverged or dirty
        """
        status = self.status(quiet=quiet)
        if status.diverge and not force:
            msg = f"Diverged: {status=}, {self.repo=}"
            raise RuntimeError(msg)
        if status.pull:
            self.git_check_call(f"pull {'--force' if force else ''} {'--quiet' if quiet else ''}")
            self.info(self.pull.__name__)

    def push(self, force: bool = False, quiet: bool = True) -> None:
        """push.

        Raises:
            CalledProcessError: if push fails
            RuntimeError: if diverged
        """
        self.commit(force=force, quiet=quiet)
        status = self.status(quiet=quiet)
        if status.push:
            if status.pull and not force:
                msg = f"Diverged: {status=}, {self.repo=}"
                raise RuntimeError(msg)
            self.git_check_call(f"push {'--force' if force else ''} {'--quiet' if quiet else ''}")
            self.info(self.push.__name__)

    def secrets(self, force: bool = False) -> int:
        """Update GitHub repository secrets."""
        if CI or DOCKER:
            return 0
        if not self.secrets_names() or force:
            self.gh_check_call(f"secret set GH_TOKEN --body {GITHUB_TOKEN}")
            if (secrets := Path.home() / "secrets/profile.d/secrets.sh").is_file():
                with tempfile.NamedTemporaryFile() as tmp:
                    subprocess.check_call(
                        f"grep -v GITHUB_ {secrets} > {tmp.name} && cd {self._path} && gh secret set -f {tmp.name}",
                        shell=True,
                    )
                    self.info(self.secrets.__name__)
        return 0

    def secrets_names(self):
        """List GitHub repository secrets names."""
        return self.gh_stdout("secret list --jq .[].name  --json name").splitlines()

    def status(self, quiet: bool = True) -> GitStatus:
        """Git status instance and fetch if necessary."""
        base = ""
        diverge = pull = push = False
        local = self.git_stdout("rev-parse @")
        self.git_check_call(f"fetch --all --tags --prune {'--quiet' if quiet else ''}")
        remote = self.git_stdout("rev-parse @{u}")

        dirty = bool(self.git_stdout("status -s"))
        if local != remote:
            # self.git_check_call(f"fetch --all --tags --prune {'--quiet' if quiet else ''}")
            base = self.git_stdout("merge-base @ @{u}")
            if local == base:
                pull = True
                diverge = dirty
            elif remote == base:
                push = True
            else:
                diverge = True
                pull = True
                push = True
        return GitStatus(base=base, dirty=dirty, diverge=diverge, local=local, pull=pull, push=push, remote=remote)

    def superproject(self) -> Path | None:
        """Git rev-parse --show-superproject-working-tree --show-toplevel."""
        if v := self.git_stdout("rev-parse --show-superproject-working-tree --show-toplevel"):
            return Path(v[0])
        return None

    def _tag(self, tag: str, quiet: bool = True) -> None:
        self.git_check_call(f"tag {tag}")
        self.git_check_call(f"push origin {tag} {'--quiet' if quiet else ''}")
        self.info(f"{self.tag.__name__}: {tag}")

    def tag(self, tag: str, quiet: bool = True) -> str | None:
        """Git tag."""
        if self.latest() == tag:
            self.warning(f"{self.tag.__name__}: {tag} -> nothing to do")
            return
        self._tag(tag, quiet=quiet)

    def sync(self):
        """Sync repository."""
        self.push()
        self.pull()

    def top(self) -> Path | None:
        """Git rev-parse --show-toplevel."""
        if v := self.git_stdout("rev-parse --show-toplevel"):
            return Path(v)
        return None


async def aioclone(
        owner: str | None = None,
        repository: str = NODEPS_PROJECT_NAME,
        path: Path | str | None = None,
) -> Path:
    """Async Clone Repository.

    Examples:
        >>> import asyncio
        >>> from nodeps import Path
        >>> from nodeps import aioclone
        >>>
        >>> with Path.tempdir() as tmp:
        ...     directory = tmp / "1" / "2" / "3"
        ...     rv = asyncio.run(aioclone("octocat", "Hello-World", path=directory))
        ...     assert (rv / "README").exists()

    Args:
        owner: github owner, None to use GIT or USER environment variable if not defined (Default: `GIT`)
        repository: github repository (Default: `PROJECT`)
        path: path to clone (Default: `repo`)

    Returns:
        Path of cloned repository
    """
    path = path or Path.cwd() / repository
    path = Path(path)
    if not path.exists():
        if not path.parent.exists():
            path.parent.mkdir()
        await aiocmd("git", "clone", GitUrl(owner, repository).url, path)
    return path


def clone(
        owner: str | None = None,
        repository: str = NODEPS_PROJECT_NAME,
        path: Path | str = None,
) -> Path:
    """Clone Repository.

    Examples:
        >>> import os
        >>> from nodeps import Path
        >>> from nodeps import clone
        >>>
        >>> with Path.tempdir() as tmp:
        ...     directory = tmp / "1" / "2" / "3"
        >>> if not os.environ.get("CI"):
        ...     rv = clone("octocat", "Hello-World", directory)
        ...     assert (rv / "README").exists()

    Args:
        owner: github owner, None to use GIT or USER environment variable if not defined (Default: `GIT`)
        repository: github repository (Default: `PROJECT`)
        path: path to clone (Default: `repo`)

    Returns:
        CompletedProcess
    """
    path = path or Path.cwd() / repository
    path = Path(path)
    if not path.exists():
        if not path.parent.exists():
            path.parent.mkdir()
        cmd("git", "clone", GitUrl(owner, repository).url, path)
    return path


def git_config_global():
    """Sets values in git global config if not set."""
    for key, value in GIT_CONFIG_GLOBAL.items():
        if subprocess.run(f"git config --global {key}", capture_output=True, shell=True).returncode != 0:
            subprocess.check_call(f"git config --global {key} {value}", shell=True)
