"""Env Module."""
from __future__ import annotations

__all__ = (
    "Env",
    "EnvBuilder",
    "parse_str",
)

import dataclasses
import ipaddress
import logging
import os
import sys
import urllib.parse
import venv
from ipaddress import IPv4Address, IPv6Address
from typing import TYPE_CHECKING, Any, ClassVar

from nodeps.modules.functions import envsh
from nodeps.modules.gh import GitUrl
from nodeps.modules.metapath import pipmetapathfinder
from nodeps.modules.path import Path

if TYPE_CHECKING:
    import types
    from urllib.parse import ParseResult

    from decouple import CONFIG  # type: ignore[attr-defined]


# noinspection LongLine,SpellCheckingInspection
@dataclasses.dataclass
class Env:
    """Environ Class.

    See Also: `Environment variables
    <https://docs.github.com/en/enterprise-cloud@latest/actions/learn-github-actions/environment-variables>`_

    If you need to use a workflow run's URL from within a job, you can combine these environment variables:
        ``$GITHUB_SERVER_URL/$GITHUB_REPOSITORY/actions/runs/$GITHUB_RUN_ID``

    If you generate a value in one step of a job, you can use the value in subsequent ``steps`` of
        the same job by assigning the value to an existing or new environment variable and then writing
        this to the ``GITHUB_ENV`` environment file, see `Commands
        <https://docs.github.com/en/enterprise-cloud@latest/actions/reference/workflow-commands-for-github-actions
        /#setting-an-environment-variable>`_.

    If you want to pass a value from a step in one job in a ``workflow`` to a step in another job in the workflow,
        you can define the value as a job output, see `Syntax
        <https://docs.github.com/en/enterprise-cloud@latest/actions/learn-github-actions/workflow-syntax-for-github
        -actions#jobsjob_idoutputs>`_.
    """

    config: CONFIG = dataclasses.field(default=None, init=False)
    """Searches for `settings.ini` and `.env` cwd up. Usage: var = Env()._config("VAR", default=True, cast=bool)."""

    CI: bool | str | None = dataclasses.field(default=None, init=False)
    """Always set to ``true`` in a GitHub Actions environment."""

    GITHUB_ACTION: str | None = dataclasses.field(default=None, init=False)
    # noinspection LongLine
    """
    The name of the action currently running, or the `id
    <https://docs.github.com/en/enterprise-cloud@latest/actions/using-workflows/workflow-syntax-for-github-actions#jobs\
        job_idstepsid>`_ of a step.

    For example, for an action, ``__repo-owner_name-of-action-repo``.

    GitHub removes special characters, and uses the name ``__run`` when the current step runs a script without an id.

    If you use the same script or action more than once in the same job,
    the name will include a suffix that consists of the sequence number preceded by an underscore.

    For example, the first script you run will have the name ``__run``, and the second script will be named ``__run_2``.

    Similarly, the second invocation of ``actions/checkout`` will be ``actionscheckout2``.
    """

    GITHUB_ACTION_PATH: Path | str | None = dataclasses.field(default=None, init=False)
    """
    The path where an action is located. This property is only supported in composite actions.

    You can use this path to access files located in the same repository as the action.

    For example, ``/home/runner/work/_actions/repo-owner/name-of-action-repo/v1``.
    """

    GITHUB_ACTION_REPOSITORY: str | None = dataclasses.field(default=None, init=False)
    """
    For a step executing an action, this is the owner and repository name of the action.

    For example, ``actions/checkout``.
    """

    GITHUB_ACTIONS: bool | str | None = dataclasses.field(default=None, init=False)
    """
    Always set to ``true`` when GitHub Actions is running the workflow.

    You can use this variable to differentiate when tests are being run locally or by GitHub Actions.
    """

    GITHUB_ACTOR: str | None = dataclasses.field(default=None, init=False)
    """
    The name of the person or app that initiated the workflow.

    For example, ``octocat``.
    """

    GITHUB_API_URL: ParseResult | str | None = dataclasses.field(default=None, init=False)
    """
    API URL.

    For example: ``https://api.github.com``.
    """

    GITHUB_BASE_REF: str | None = dataclasses.field(default=None, init=False)
    """
    The name of the base ref or target branch of the pull request in a workflow run.

    This is only set when the event that triggers a workflow run is either ``pull_request`` or ``pull_request_target``.

    For example, ``main``.
    """

    GITHUB_ENV: Path | str | None = dataclasses.field(default=None, init=False)
    """
    The path on the runner to the file that sets environment variables from workflow commands.

    This file is unique to the current step and changes for each step in a job.

    For example, ``/home/runner/work/_temp/_runner_file_commands/set_env_87406d6e-4979-4d42-98e1-3dab1f48b13a``.

    For more information, see `Workflow commands for GitHub Actions.
    <https://docs.github.com/en/enterprise-cloud@latest/actions/using-workflows/workflow-commands-for-github-actions
    #setting-an-environment-variable>`_
    """

    GITHUB_EVENT_NAME: str | None = dataclasses.field(default=None, init=False)
    """
    The name of the event that triggered the workflow.

    For example, ``workflow_dispatch``.
    """

    GITHUB_EVENT_PATH: Path | str | None = dataclasses.field(default=None, init=False)
    """
    The path to the file on the runner that contains the full event webhook payload.

    For example, ``/github/workflow/event.json``.
    """

    GITHUB_GRAPHQL_URL: ParseResult | str | None = dataclasses.field(default=None, init=False)
    """
    Returns the GraphQL API URL.

    For example: ``https://api.github.com/graphql``.
    """

    GITHUB_HEAD_REF: str | None = dataclasses.field(default=None, init=False)
    """
    The head ref or source branch of the pull request in a workflow run.

    This property is only set when the event that triggers a workflow run is either
    ``pull_request`` or ``pull_request_target``.

    For example, ``feature-branch-1``.
    """

    GITHUB_JOB: str | None = dataclasses.field(default=None, init=False)
    """
    The `job_id
    <https://docs.github.com/en/enterprise-cloud@latest/actions/reference/workflow-syntax-for-github-actions
    #jobsjob_id>`_
    of the current job.

    For example, ``greeting_job``.
    """

    GITHUB_PATH: Path | str | None = dataclasses.field(default=None, init=False)
    """
    The path on the runner to the file that sets system PATH variables from workflow commands.
    This file is unique to the current step and changes for each step in a job.

    For example, ``/home/runner/work/_temp/_runner_file_commands/add_path_899b9445-ad4a-400c-aa89-249f18632cf5``.

    For more information, see `Workflow commands for GitHub Actions.
    <https://docs.github.com/en/enterprise-cloud@latest/actions/using-workflows/workflow-commands-for-github-actions
    #adding-a-system-path>`_
    """

    GITHUB_REF: str | None = dataclasses.field(default=None, init=False)
    """
    The branch or tag ref that triggered the workflow run.

    For branches this is the format ``refs/heads/<branch_name>``,
    for tags it is ``refs/tags/<tag_name>``,
    and for pull requests it is ``refs/pull/<pr_number>/merge``.

    This variable is only set if a branch or tag is available for the event type.

    For example, ``refs/heads/feature-branch-1``.
    """

    GITHUB_REF_NAME: str | None = dataclasses.field(default=None, init=False)
    """
    The branch or tag name that triggered the workflow run.

    For example, ``feature-branch-1``.
    """

    GITHUB_REF_PROTECTED: bool | str | None = dataclasses.field(default=None, init=False)
    """
    ``true`` if branch protections are configured for the ref that triggered the workflow run.
    """

    GITHUB_REF_TYPE: str | None = dataclasses.field(default=None, init=False)
    """
    The type of ref that triggered the workflow run.

    Valid values are ``branch`` or ``tag``.

    For example, ``branch``.
    """

    GITHUB_REPOSITORY: str | None = dataclasses.field(default=None, init=False)
    """
    The owner and repository name.

    For example, ``octocat/Hello-World``.
    """

    GITHUB_REPOSITORY_OWNER: str | None = dataclasses.field(default=None, init=False)
    """
    The repository owner's name.

    For example, ``octocat``.
    """

    GITHUB_RETENTION_DAYS: str | None = dataclasses.field(default=None, init=False)
    """
    The number of days that workflow run logs and artifacts are kept.

    For example, ``90``.
    """

    GITHUB_RUN_ATTEMPT: str | None = dataclasses.field(default=None, init=False)
    """
    A unique number for each attempt of a particular workflow run in a repository.

    This number begins at ``1`` for the workflow run's first attempt, and increments with each re-run.

    For example, ``3``.
    """

    GITHUB_RUN_ID: str | None = dataclasses.field(default=None, init=False)
    """
    A unique number for each workflow run within a repository.

    This number does not change if you re-run the workflow run.

    For example, ``1658821493``.
    """

    GITHUB_RUN_NUMBER: str | None = dataclasses.field(default=None, init=False)
    """
    A unique number for each run of a particular workflow in a repository.

    This number begins at ``1`` for the workflow's first run, and increments with each new run.
    This number does not change if you re-run the workflow run.

    For example, ``3``.
    """

    GITHUB_SERVER_URL: ParseResult | str | None = dataclasses.field(default=None, init=False)
    """
    The URL of the GitHub Enterprise Cloud server.

    For example: ``https://github.com``.
    """

    GITHUB_SHA: str | None = dataclasses.field(default=None, init=False)
    """
    The commit SHA that triggered the workflow.

    The value of this commit SHA depends on the event that triggered the workflow.
    For more information, see `Events that trigger workflows.
    <https://docs.github.com/en/enterprise-cloud@latest/actions/using-workflows/events-that-trigger-workflows>`_

    For example, ``ffac537e6cbbf934b08745a378932722df287a53``.
    """

    GITHUB_WORKFLOW: Path | str | None = dataclasses.field(default=None, init=False)
    """
    The name of the workflow.

    For example, ``My test workflow``.

    If the workflow file doesn't specify a name,
    the value of this variable is the full path of the workflow file in the repository.
    """

    GITHUB_WORKSPACE: Path | str | None = dataclasses.field(default=None, init=False)
    """
    The default working directory on the runner for steps, and the default location of your repository
    when using the `checkout <https://github.com/actions/checkout>`_ action.

    For example, ``/home/runner/work/my-repo-name/my-repo-name``.
    """

    RUNNER_ARCH: str | None = dataclasses.field(default=None, init=False)
    """
    The architecture of the runner executing the job.

    Possible values are ``X86``, ``X64``, ``ARM``, or ``ARM64``.

    For example, ``X86``.
    """

    RUNNER_NAME: str | None = dataclasses.field(default=None, init=False)
    """
    The name of the runner executing the job.

    For example, ``Hosted Agent``.
    """

    RUNNER_OS: str | None = dataclasses.field(default=None, init=False)
    """
    The operating system of the runner executing the job.

    Possible values are ``Linux``, ``Windows``, or ``macOS``.

    For example, ``Linux``.
    """

    RUNNER_TEMP: Path | str | None = dataclasses.field(default=None, init=False)
    """
    The path to a temporary directory on the runner.

    This directory is emptied at the beginning and end of each job.

    Note that files will not be removed if the runner's user account does not have permission to delete them.

    For example, ``_temp``.
    """

    RUNNER_TOOL_CACHE: str | None = dataclasses.field(default=None, init=False)
    # noinspection LongLine
    """
    The path to the directory containing preinstalled tools for GitHub-hosted runners.

    For more information, see `About GitHub-hosted runners.
    <https://docs.github.com/en/enterprise-cloud@latest/actions/reference/specifications-for-github-hosted-runners
    /#supported-software>`_

    `Ubuntu latest <https://github.com/actions/virtual-environments/blob/main/images/linux/Ubuntu2004-Readme.md>`_
    `macOS latest <https://github.com/actions/virtual-environments/blob/main/images/macos/macos-11-Readme.md>`_

    For example, ``C:/hostedtoolcache/windows``.
    """

    COMMAND_MODE: str | None = dataclasses.field(default=None, init=False)
    HOME: str | None = dataclasses.field(default=None, init=False)
    IPYTHONENABLE: str | None = dataclasses.field(default=None, init=False)
    LC_TYPE: str | None = dataclasses.field(default=None, init=False)
    LOGNAME: str | None = dataclasses.field(default=None, init=False)
    OLDPWD: str | None = dataclasses.field(default=None, init=False)
    PATH: str | None = dataclasses.field(default=None, init=False)
    PS1: str | None = dataclasses.field(default=None, init=False)
    PWD: str | None = dataclasses.field(default=None, init=False)
    PYCHARM_DISPLAY_PORT: str | None = dataclasses.field(default=None, init=False)
    PYCHARM_HOSTED: str | None = dataclasses.field(default=None, init=False)
    PYCHARM_MATPLOTLIB_INDEX: str | None = dataclasses.field(default=None, init=False)
    PYCHARM_MATPLOTLIB_INTERACTIVE: str | None = dataclasses.field(default=None, init=False)
    PYCHARM_PROPERTIES: str | None = dataclasses.field(default=None, init=False)
    PYCHARM_VM_OPTIONS: str | None = dataclasses.field(default=None, init=False)
    PYDEVD_LOAD_VALUES_ASYNC: str | None = dataclasses.field(default=None, init=False)
    PYTHONIOENCODING: str | None = dataclasses.field(default=None, init=False)
    PYTHONPATH: str | None = dataclasses.field(default=None, init=False)
    PYTHONUNBUFFERED: str | None = dataclasses.field(default=None, init=False)
    SHELL: str | None = dataclasses.field(default=None, init=False)
    SSH_AUTH_SOCK: str | None = dataclasses.field(default=None, init=False)
    SUDO_USER: str | None = dataclasses.field(default=None, init=False)
    TMPDIR: str | None = dataclasses.field(default=None, init=False)
    XPC_FLAGS: str | None = dataclasses.field(default=None, init=False)
    XPC_SERVICE_NAME: str | None = dataclasses.field(default=None, init=False)
    __CFBundleIdentifier: str | None = dataclasses.field(default=None, init=False)
    __CF_USER_TEXT_ENCODING: str | None = dataclasses.field(default=None, init=False)

    LOGURU_LEVEL: str | None = dataclasses.field(default="DEBUG", init=False)
    LOG_LEVEL: int | str | None = dataclasses.field(default="DEBUG", init=False)

    _parse_as_int: ClassVar[tuple[str, ...]] = (
        "GITHUB_RUN_ATTEMPT",
        "GITHUB_RUN_ID",
        "GITHUB_RUN_NUMBER",
    )
    _parse_as_int_suffix: ClassVar[tuple[str, ...]] = (
        "_GID",
        "_JOBS",
        "_PORT",
        "_UID",
    )
    parsed: dataclasses.InitVar[bool] = True

    def __post_init__(self, parsed: bool) -> None:
        """Instance of Env class.

        Examples:
            >>> import logging
            >>> from nodeps import Env, MACOS, LOCAL
            >>> from nodeps import Path
            >>>
            >>> env = Env()
            >>> assert env.config("DECOUPLE_CONFIG_TEST") == 'True'
            >>> assert env.config("DECOUPLE_CONFIG_TEST",  cast=bool) == True
            >>> assert env.LOG_LEVEL == logging.DEBUG
            >>> if MACOS and LOCAL:
            ...     assert isinstance(env.PWD, Path)
            ...     assert "PWD" in env

        Args:
            parsed: Parse the environment variables using :func:`nodeps.parse_str`,
                except :func:`Env.as_int` (default: True)
        """
        envsh()
        self.__dict__.update({k: self.as_int(k, v) for k, v in os.environ.items()} if parsed else os.environ)
        self.LOG_LEVEL = getattr(logging, self.LOG_LEVEL.upper() if isinstance(self.LOG_LEVEL, str) else self.LOG_LEVEL)

        if path := (Path.cwd() / "settings.ini").find_up():
            with pipmetapathfinder():
                import decouple  # type: ignore[attr-defined]

                self.config = decouple.Config(decouple.RepositoryIni(path.absolute()))

    def __contains__(self, item):
        """Check if item is in self.__dict__."""
        return item in self.__dict__

    def __getattr__(self, name: str) -> bool | Path | ParseResult | IPv4Address | IPv6Address | int | str | None:
        """Get attribute from self.__dict__ if exists, otherwise return None."""
        if name in self:
            return self.__dict__[name]
        return None

    def __getattribute__(self, name: str) -> bool | Path | ParseResult | IPv4Address | IPv6Address | int | str | None:
        """Get attribute from self.__dict__ if exists, otherwise return None."""
        try:
            return super().__getattribute__(name)
        except AttributeError:
            return None

    def __getitem__(self, item: str) -> bool | Path | ParseResult | IPv4Address | IPv6Address | int | str | None:
        """Get item from self.__dict__ if exists, otherwise return None."""
        return self.__getattr__(item)

    @classmethod
    def as_int(cls, key: str, value: str = "") -> bool | Path | ParseResult | IPv4Address | IPv6Address | int | str:
        """Parse as int if environment variable should be forced to be parsed as int checking if:.

            - has value,
            - key in :data:`Env._parse_as_int` or
            - key ends with one of the items in :data:`Env._parse_as_int_suffix`.

        Args:
            key: Environment variable name.
            value: Environment variable value (default: "").

        Returns:
            int, if key should be parsed as int and has value, otherwise according to :func:`parse_str`.
        """
        convert = False
        if value:
            if key in cls._parse_as_int:
                convert = True
            else:
                for item in cls._parse_as_int_suffix:
                    if key.endswith(item):
                        convert = True
        return int(value) if convert and value.isnumeric() else parse_str(value)

    @staticmethod
    def parse_as_bool(
            variable: str = "USER",
    ) -> bool | Path | ParseResult | IPv4Address | IPv6Address | int | str | None:
        """Parses variable from environment 1 and 0 as bool instead of int.

        Parses:
            - bool: 1, 0, True, False, yes, no, on, off (case insensitive)
            - int: integer only numeric characters but 1 and 0 or SUDO_UID or SUDO_GID
            - ipaddress: ipv4/ipv6 address
            - url: if "//" or "@" is found it will be parsed as url
            - path: start with / or ~ or .
            - others as string

        Arguments:
            variable: variable name to parse from environment (default: USER)

        Examples:
            >>> from nodeps import Path, MACOS, LOCAL
            >>> from nodeps import Env
            >>>
            >>> if MACOS and LOCAL:
            ...     assert isinstance(Env.parse_as_bool(), str)
            >>>
            >>> os.environ['FOO'] = '1'
            >>> assert Env.parse_as_bool("FOO") is True
            >>>
            >>> os.environ['FOO'] = '0'
            >>> assert Env.parse_as_bool("FOO") is False
            >>>
            >>> os.environ['FOO'] = 'TrUe'
            >>> assert Env.parse_as_bool("FOO") is True
            >>>
            >>> os.environ['FOO'] = 'OFF'
            >>> assert Env.parse_as_bool("FOO") is False
            >>>
            >>> os.environ['FOO'] = '~/foo'
            >>> assert Env.parse_as_bool("FOO") == Path('~/foo')
            >>>
            >>> os.environ['FOO'] = '/foo'
            >>> assert Env.parse_as_bool("FOO") == Path('/foo')
            >>>
            >>> os.environ['FOO'] = './foo'
            >>> assert Env.parse_as_bool("FOO") == Path('./foo')
            >>>
            >>> os.environ['FOO'] = './foo'
            >>> assert Env.parse_as_bool("FOO") == Path('./foo')
            >>>
            >>> v = "https://github.com"
            >>> os.environ['FOO'] = v
            >>> assert Env.parse_as_bool("FOO").geturl() == v
            >>>
            >>> v = "git@github.com"
            >>> os.environ['FOO'] = v
            >>> assert Env.parse_as_bool("FOO").geturl() == v
            >>>
            >>> v = "0.0.0.0"
            >>> os.environ['FOO'] = v
            >>> assert Env.parse_as_bool("FOO").exploded == v
            >>>
            >>> os.environ['FOO'] = "::1"
            >>> assert Env.parse_as_bool("FOO").exploded.endswith(":0001")
            >>>
            >>> v = "2"
            >>> os.environ['FOO'] = v
            >>> assert Env.parse_as_bool("FOO") == int(v)
            >>>
            >>> v = "2.0"
            >>> os.environ['FOO'] = v
            >>> assert Env.parse_as_bool("FOO") == v
            >>>
            >>> del os.environ['FOO']
            >>> assert Env.parse_as_bool("FOO") is None

        Returns:
            None
        """
        if value := os.environ.get(variable):
            if variable in ("SUDO_UID", "SUDO_GID"):
                return int(value)
            if variable == "PATH":
                return value
            return parse_str(value)
        return value

    @classmethod
    def parse_as_int(
            cls,
            name: str = "USER",
    ) -> bool | Path | ParseResult | IPv4Address | IPv6Address | int | str | None:
        """Parses variable from environment using :func:`mreleaser.parse_str`,.

        except ``SUDO_UID`` or ``SUDO_GID`` which are parsed as int instead of bool.

        Arguments:
            name: variable name to parse from environment (default: USER)

        Examples:
            >>> from nodeps import Path, MACOS, LOCAL
            >>> from nodeps import Env
            >>>
            >>> if MACOS and LOCAL:
            ...     assert isinstance(Env.parse_as_int(), str)
            >>>
            >>> os.environ['FOO'] = '1'
            >>> assert Env.parse_as_int("FOO") is True
            >>>
            >>> os.environ['FOO'] = '0'
            >>> assert Env.parse_as_int("FOO") is False
            >>>
            >>> os.environ['FOO'] = 'TrUe'
            >>> assert Env.parse_as_int("FOO") is True
            >>>
            >>> os.environ['FOO'] = 'OFF'
            >>> assert Env.parse_as_int("FOO") is False
            >>>
            >>> os.environ['FOO'] = '~/foo'
            >>> assert Env.parse_as_int("FOO") == Path('~/foo')
            >>>
            >>> os.environ['FOO'] = '/foo'
            >>> assert Env.parse_as_int("FOO") == Path('/foo')
            >>>
            >>> os.environ['FOO'] = './foo'
            >>> assert Env.parse_as_int("FOO") == Path('./foo')
            >>>
            >>> os.environ['FOO'] = './foo'
            >>> assert Env.parse_as_int("FOO") == Path('./foo')
            >>>
            >>> v = "https://github.com"
            >>> os.environ['FOO'] = v
            >>> assert Env.parse_as_int("FOO").geturl() == v
            >>>
            >>> v = "git@github.com"
            >>> os.environ['FOO'] = v
            >>> assert Env.parse_as_int("FOO").geturl() == v
            >>>
            >>> v = "0.0.0.0"
            >>> os.environ['FOO'] = v
            >>> assert Env.parse_as_int("FOO").exploded == v
            >>>
            >>> os.environ['FOO'] = "::1"
            >>> assert Env.parse_as_int("FOO").exploded.endswith(":0001")
            >>>
            >>> v = "2"
            >>> os.environ['FOO'] = v
            >>> assert Env.parse_as_int("FOO") == int(v)
            >>>
            >>> v = "2.0"
            >>> os.environ['FOO'] = v
            >>> assert Env.parse_as_int("FOO") == v
            >>>
            >>> del os.environ['FOO']
            >>> assert Env.parse_as_int("FOO") is None
            >>>
            >>> if not os.environ.get("CI"):
            ...     assert isinstance(Env.parse_as_int("PATH"), str)

        Returns:
            Value parsed
        """
        if value := os.environ.get(name):
            return cls.as_int(name, value)
        return value


@dataclasses.dataclass
class EnvBuilder(venv.EnvBuilder):
    """Wrapper for :class:`venv.EnvBuilder`.

    Changed defaults for: `prompt`` `symlinks` and `with_pip`, adds `env_dir` to `__init__` arguments.

    Post install in :py:meth:`.post_setup`.

    This class exists to allow virtual environment creation to be
    customized. The constructor parameters determine the builder's
    behaviour when called upon to create a virtual environment.

    By default, the builder makes the system (global) site-packages dir *un*available to the created environment.

    If invoked using the Python -m option, the default is to use copying
    on Windows platforms but symlinks elsewhere. If instantiated some
    other way, the default is to *not* use symlinks (changed with the wrapper to use symlinks always).

    Attributes:
        system_site_packages: bool
            If True, the system (global) site-packages dir is available to created environments.
        clear: bool
            If True, delete the contents of the environment directory if it already exists, before environment creation.
        symlinks: bool
            If True, attempt to symlink rather than copy files into virtual environment.
        upgrade: bool
            If True, upgrade an existing virtual environment.
        with_pip: bool
            If True, ensure pip is installed in the virtual environment.
        prompt: str
            Alternative terminal prefix for the environment.
        upgrade_deps: bool
            Update the base venv modules to the latest on PyPI (python 3.9+).
        context: Simplenamespace
            The information for the environment creation request being processed.
        env_dir: bool
            The target directory to create an environment in.
    """

    system_site_packages: bool = False
    clear: bool = False
    symlinks: bool = True
    upgrade: bool = True
    """Upgrades scripts and run :class:`venv.EnvBuilder.post_setup`."""
    with_pip: bool = True
    prompt: str | None = "."
    """To use basename use '.'."""
    upgrade_deps: bool = True
    """upgrades :data:`venv.CORE_VENV_DEPS`."""
    env_dir: Path | str | None = "venv"
    context: types.SimpleNamespace | None = dataclasses.field(default=None, init=False)

    def __post_init__(self):
        """Initialize the environment builder and also creates the environment is does not exist."""
        super().__init__(
            system_site_packages=self.system_site_packages,
            clear=self.clear,
            symlinks=self.symlinks,
            upgrade=self.upgrade,
            with_pip=self.with_pip,
            prompt=self.prompt,
            **({"upgrade_deps": self.upgrade_deps} if sys.version_info >= (3, 9) else {}),
        )
        if self.env_dir:
            self.env_dir = Path(self.env_dir).absolute()
            if self.env_dir.exists():
                self.ensure_directories()
            else:
                self.create(self.env_dir)

    def create(self, env_dir: Path | str | None = None) -> None:
        """Create a virtual environment in a directory.

        Args:
            env_dir: The target directory to create an environment in.
        """
        self.env_dir = env_dir or self.env_dir
        super().create(self.env_dir)

    def ensure_directories(self, env_dir: Path | str | None = None) -> types.SimpleNamespace:
        """Create the directories for the environment.

        Args:
            env_dir: The target directory to create an environment in.

        Returns:
            A context object which holds paths in the environment, for use by subsequent logic.
        """
        self.context = super().ensure_directories(env_dir or self.env_dir)
        return self.context

    def post_setup(self, context: types.SimpleNamespace | None = None) -> None:
        """Hook for post-setup modification of the venv.

        Subclasses may install additional packages or scripts here, add activation shell scripts, etc.

        Args:
            context: The information for the environment creation request being processed.
        """


def parse_str(  # noqa: PLR0911
        data: Any | None = None,
) -> bool | GitUrl | Path | ParseResult | IPv4Address | IPv6Address | int | str | None:
    """Parses str or data.__str__().

    Parses:
        - bool: 1, 0, True, False, yes, no, on, off (case insensitive)
        - int: integer only numeric characters but 1 and 0
        - ipaddress: ipv4/ipv6 address
        - url: if "://" or "@" is found it will be parsed as url
        - path: if "." or start with "/" or "~" or "." and does contain ":"
        - others as string

    Arguments:
        data: variable name to parse from environment (default: USER)

    Examples:
        >>> import os
        >>> from nodeps import Path
        >>> from nodeps import parse_str
        >>>
        >>> assert parse_str() is None
        >>>
        >>> assert parse_str("1") is True
        >>> assert parse_str("0") is False
        >>> assert parse_str("TrUe") is True
        >>> assert parse_str("OFF") is False
        >>>
        >>> u = "https://github.com/user/repo"
        >>> assert parse_str(u).url == u
        >>> u = "git@github.com:user/repo"
        >>> assert parse_str(u).url == u
        >>> u = "https://github.com"
        >>> assert parse_str(u).geturl() == u
        >>> u = "git@github.com"
        >>> assert parse_str(u).geturl() == u
        >>>
        >>> assert parse_str("~/foo") == Path('~/foo')
        >>> assert parse_str("/foo") == Path('/foo')
        >>> assert parse_str("./foo") == Path('foo')
        >>> assert parse_str(".") == Path('.')
        >>> assert parse_str(Path()) == Path()
        >>>
        >>> assert parse_str("0.0.0.0").exploded == "0.0.0.0"
        >>> assert parse_str("::1").exploded.endswith(":0001")
        >>>
        >>> assert parse_str("2") == 2
        >>> assert parse_str("2.0") == "2.0"
        >>> assert parse_str("/usr/share/man:") == "/usr/share/man:"
        >>> if not os.environ.get("CI"):
        ...     assert isinstance(parse_str(os.environ.get("PATH")), str)

    Returns:
        None
    """
    if data is not None:
        if not isinstance(data, str):
            data = str(data)

        if data.lower() in ["1", "true", "yes", "on"]:
            return True
        if data.lower() in ["0", "false", "no", "off"]:
            return False
        if "://" in data or "@" in data:
            return p if (p := GitUrl(data)).valid else urllib.parse.urlparse(data)
        if (
                (
                        data and data[0] in ["/", "~"] or (
                        len(data) >= 2 and f"{data[0]}{data[1]}" == "./")  # noqa: PLR2004
                )
                and ":" not in data
        ) or data == ".":
            return Path(data)
        try:
            return ipaddress.ip_address(data)
        except ValueError:
            if data.isnumeric():
                return int(data)
    return data


venv.CORE_VENV_DEPS = ["build", "ipython", "pip", "setuptools", "wheel"]
venv.EnvBuilder = EnvBuilder
