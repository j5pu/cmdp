"""CMDp functions module."""
__all__ = (
    "EXECUTABLE",
    "EXECUTABLE_SITE",
    "LINUX",
    "MACOS",
    "PW_ROOT",
    "PW_USER",
    "aioclone",
    "aiocmd",
    "aiocommand",
    "clone",
    "cmd",
    "cmdrun",
    "cmdsudo",
    "command",
    "returncode",
    "stdout",
    "syssudo",
    "TempDir",
)

import asyncio
import contextlib
import copy
import fnmatch
import getpass
import grp
import importlib.metadata
import importlib.util
import os
import pwd
import re
import shutil
import subprocess
import sys
import sysconfig
import tempfile
import types
import venv
from pathlib import Path, PurePath
from typing import Any, AnyStr, Callable, Iterable, Optional, ParamSpec, TypeVar, Union, cast

import loguru
import packaging.requirements
import toml

from ..env import USER
from .classes import CalledProcessError, CmdError, GroupUser, TempDir, Top
from .constants import LOGGER_DEFAULT_FMT
from .enums import FileName, PathIs, PathSuffix
from .errors import CommandNotFound, InvalidArgument
from .typings import AnyPath, ExcType, StrOrBytesPath
from .variables import PPIP_DATA

EXECUTABLE = Path(sys.executable)
EXECUTABLE_SITE = Path(EXECUTABLE).resolve()
LINUX = sys.platform == "linux"
"""Is Linux? sys.platform == 'linux'"""
MACOS = sys.platform == "darwin"
"""Is macOS? sys.platform == 'darwin'"""
PW_ROOT = pwd.getpwnam("root")
PW_USER = pwd.getpwnam(os.environ["USER"])

P = ParamSpec("P")
T = TypeVar("T")


async def aioclone(owner: str | None = None, repo: str = "ppip", scheme: GitScheme = GIT_DEFAULT_SCHEME,
                   path: Path | str = None) -> subprocess.CompletedProcess:
    """Async Clone Repository.

    Examples:
        >>> import asyncio
        >>> from pproj import TempDir
        >>> from gitp import aioclone
        >>>
        >>> with TempDir() as tmp:
        ...     directory = tmp / "1" / "2" / "3"
        ...     rv = asyncio.run(aioclone("octocat", "Hello-World", path=directory))
        ...     assert rv.returncode == 0
        ...     assert (directory / "README").exists()

    Args:
        owner: github owner, None to use GIT or USER environment variable if not defined (Default: `GIT`)
        repo: github repository (Default: `PROJECT`)
        scheme: url scheme (Default: "https")
        path: path to clone (Default: `repo`)

    Returns:
        CompletedProcess
    """
    path = path or Path.cwd() / repo
    path = Path(path)
    if not path.exists():
        if not path.parent.exists():
            path.parent.mkdir()
        return await aiocmd("git", "clone", OwnerRepo(owner, repo, scheme).url.url, path)
    return None


async def aiocmd(*args, **kwargs) -> subprocess.CompletedProcess:
    """Async Exec Command.

    Examples:
        >>> import asyncio
        >>> from ppip.utils.classes import TempDir
        >>> with TempDir() as tmp:
        ...     rv = asyncio.run(aiocmd("git", "clone", "https://github.com/octocat/Hello-World.git", cwd=tmp))
        ...     assert rv.returncode == 0
        ...     assert (tmp / "Hello-World" / "README").exists()

    Args:
        *args: command and args
        **kwargs: subprocess.run kwargs

    Raises:
        JetBrainsError

    Returns:
        None
    """
    proc = await asyncio.create_subprocess_exec(
        *args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, **kwargs
    )

    out, err = await proc.communicate()
    completed = subprocess.CompletedProcess(
        args, returncode=proc.returncode, stdout=out.decode() if out else None, stderr=err.decode() if err else None
    )
    if completed.returncode != 0:
        raise CmdError(completed)
    return completed


async def aiocommand(
    data: str | list, decode: bool = True, utf8: bool = False, lines: bool = False
) -> subprocess.CompletedProcess:
    """Asyncio run cmd.

    Args:
        data: command.
        decode: decode and strip output.
        utf8: utf8 decode.
        lines: split lines.

    Returns:
        CompletedProcess.
    """
    proc = await asyncio.create_subprocess_shell(
        data, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, loop=asyncio.get_running_loop()
    )
    out, err = await proc.communicate()
    if decode:
        out = out.decode().rstrip(".\n")
        err = err.decode().rstrip(".\n")
    elif utf8:
        out = out.decode("utf8").strip()
        err = err.decode("utf8").strip()

    out = out.splitlines() if lines else out

    return subprocess.CompletedProcess(data, proc.returncode, out, cast(Any, err))


def clone(owner: str | None = None, repo: str = "ppip", scheme: GitScheme = GIT_DEFAULT_SCHEME,
          path: Path | str = None) -> subprocess.CompletedProcess | None:
    """Clone Repository.

    Examples:
        >>> import os
        >>> from pproj import TempDir
        >>> from gitp import clone
        >>>
        >>> with TempDir() as tmp:
        ...     directory = tmp / "1" / "2" / "3"
        >>> if not os.environ.get("CI"):
        ...     rv = clone("octocat", "Hello-World", "git+ssh", directory)
        ...     assert rv.returncode == 0
        ...     assert (directory / "README").exists()

    Args:
        owner: github owner, None to use GIT or USER environment variable if not defined (Default: `GIT`)
        repo: github repository (Default: `PROJECT`)
        scheme: url scheme (Default: "https")
        path: path to clone (Default: `repo`)

    Returns:
        CompletedProcess
    """
    path = path or Path.cwd() / repo
    path = Path(path)
    if not path.exists():
        if not path.parent.exists():
            path.parent.mkdir()
        return cmd("git", "clone", OwnerRepo(owner, repo, scheme).url.url, path)
    return None

def cmd(*args, **kwargs) -> subprocess.CompletedProcess:
    """Exec Command.

    Examples:
        >>> from ppip.utils.classes import TempDir
        >>> with TempDir() as tmp:
        ...     rv = cmd("git", "clone", "https://github.com/octocat/Hello-World.git", tmp)
        ...     assert rv.returncode == 0
        ...     assert (tmp / "README").exists()

    Args:
        *args: command and args
        **kwargs: subprocess.run kwargs

    Raises:
        CmdError

    Returns:
        None
    """
    completed = subprocess.run(args, **kwargs, capture_output=True, text=True)

    if completed.returncode != 0:
        raise CmdError(completed)
    return completed


def cmdrun(
    data: Iterable, exc: bool = False, lines: bool = True, shell: bool = True, py: bool = False, pysite: bool = True
) -> subprocess.CompletedProcess | int | list | str:
    """
    Runs a cmd.

    Examples:
        >>> import ppip
        >>> from ppip.utils.functions import cmdrun
        >>> from ppip.utils.functions import tox
        >>>
        >>> cmdrun('ls a')  # doctest: +ELLIPSIS
        CompletedProcess(args='ls a', returncode=..., stdout=[], stderr=[...])
        >>> assert 'Requirement already satisfied' in cmdrun('pip install pip', py=True).stdout[0]
        >>> cmdrun('ls a', shell=False, lines=False)  # doctest: +ELLIPSIS
        CompletedProcess(args=['ls', 'a'], returncode=..., stdout='', stderr=...)
        >>> cmdrun('echo a', lines=False)  # Extra '\' added to avoid docstring error.
        CompletedProcess(args='echo a', returncode=0, stdout='a\\n', stderr='')
        >>> assert "venv" not in cmdrun("sysconfig", py=True, lines=False).stdout
        >>> if not tox:
        ...     import sysconfig; print(sysconfig.get_paths())
        ...     print("No tox")
        ...     print(__file__)
        ...     assert "venv" in cmdrun("sysconfig", py=True, pysite=False, lines=False).stdout

    Args:
        data: command.
        exc: raise exception.
        lines: split lines so ``\\n`` is removed from all lines (extra '\' added to avoid docstring error).
        py: runs with python executable.
        shell: expands shell variables and one line (shell True expands variables in shell).
        pysite: run on site python if running on a VENV.

    Returns:
        Union[CompletedProcess, int, list, str]: Completed process output.

    Raises:
        CmdError:
    """
    if py:
        m = "-m"
        if isinstance(data, str) and data.startswith("/"):
            m = ""
        data = f"{EXECUTABLE_SITE if pysite else EXECUTABLE} {m} {data}"
    elif not shell:
        data = toiter(data)

    text = not lines

    proc = subprocess.run(data, shell=shell, capture_output=True, text=text)

    def std(out=True):
        if out:
            if lines:
                return proc.stdout.decode("utf-8").splitlines()
            else:
                # return proc.stdout.rstrip('.\n')
                return proc.stdout
        else:
            if lines:
                return proc.stderr.decode("utf-8").splitlines()
            else:
                # return proc.stderr.decode("utf-8").rstrip('.\n')
                return proc.stderr

    rv = subprocess.CompletedProcess(proc.args, proc.returncode, std(), std(False))
    if rv.returncode != 0 and exc:
        raise CmdError(rv)
    return rv


def cmdsudo(*args, user: str = "root", **kwargs) -> subprocess.CompletedProcess | None:
    """
    Run Program with sudo if user is different that the current user

    Arguments:
        *args: command and args to run
        user: run as user (Default: False)
        **kwargs: subprocess.run kwargs

    Returns:
        CompletedProcess if the current user is not the same as user, None otherwise
    """
    if not ami(user):
        return cmd(["sudo", "-u", user, *args], **kwargs)
    return None


def command(*args, **kwargs) -> subprocess.CompletedProcess:
    """
    Exec Command with the following defaults compared to :func:`subprocess.run`:

        - capture_output=True
        - text=True
        - check=True

    Examples:
        >>> from ppip.utils.classes import TempDir
        >>> with TempDir() as tmp:
        ...     rv = command("git", "clone", "https://github.com/octocat/Hello-World.git", tmp)
        ...     assert rv.returncode == 0
        ...     assert (tmp / ".git").exists()

    Args:
        *args: command and args
        **kwargs: `subprocess.run` kwargs

    Raises:
        CmdError

    Returns:
        None
    """

    completed = subprocess.run(args, **kwargs, capture_output=True, text=True)

    if completed.returncode != 0:
        raise CalledProcessError(completed=completed)
    return completed

def returncode(c: str | list[str], shell: bool = True) -> int:
    """
    Runs command in shell and returns returncode showing stdout and stderr

    No exception is raised

    Examples:
        >>> from ppip.utils.functions import returncode
        >>>
        >>> assert returncode("ls /bin/ls") == 0
        >>> assert returncode("ls foo") == 1

    Arguments:
        c: command to run
        shell: run in shell (default: True)

    Returns:
        return code

    """
    return subprocess.call(c, shell=shell)


def stdout(shell: AnyStr, keepends: bool = False, split: bool = False) -> list[str] | str | None:
    """Return stdout of executing cmd in a shell or None if error.

    Execute the string 'cmd' in a shell with 'subprocess.getstatusoutput' and
    return a stdout if success. The locale encoding is used
    to decode the output and process newlines.

    A trailing newline is stripped from the output.

    Examples:
        >>> from pproj.project import stdout
        >>>
        >>> stdout("ls /bin/ls")
        '/bin/ls'
        >>> stdout("true")
        ''
        >>> stdout("ls foo")
        >>> stdout("ls /bin/ls", split=True)
        ['/bin/ls']

    Args:
        shell: command to be executed
        keepends: line breaks when ``split`` if true, are not included in the resulting list unless keepends
            is given and true.
        split: return a list of the stdout lines in the string, breaking at line boundaries.(default: False)

    Returns:
        Stdout or None if error.
    """
    exitcode, data = subprocess.getstatusoutput(shell)

    if exitcode == 0:
        if split:
            return data.splitlines(keepends=keepends)
        return data
    return None

def syssudo(user: str = "root") -> subprocess.CompletedProcess | None:
    """
    Rerun Program with sudo ``sys.executable`` and ``sys.argv`` if user is different that the current user

    Arguments:
        user: run as user (Default: False)

    Returns:
        CompletedProcess if the current user is not the same as user, None otherwise
    """
    if not ami(user):
        return cmd(["sudo", "-u", user, sys.executable, *sys.argv])
    return None


class TempDir(tempfile.TemporaryDirectory):
    """Wrapper for :class:`tempfile.TemporaryDirectory` that provides Path-like.

    Examples:
        >>> from pproj.project import TempDir
        >>> from pproj.project import MACOS
        >>> with TempDir() as tmp:
        ...     if MACOS:
        ...         assert tmp.parts[1] == "var"
        ...         assert tmp.resolve().parts[1] == "private"
    """

    def __enter__(self) -> Path:
        """Return the path of the temporary directory.

        Returns:
            Path of the temporary directory
        """
        return Path(self.name)

