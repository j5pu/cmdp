"""Functions Module."""
from __future__ import annotations

__all__ = (
    "aioclosed",
    "aiocmd",
    "aiocommand",
    "aiodmg",
    "aiogz",
    "aioloop",
    "aioloopid",
    "aiorunning",
    "allin",
    "ami",
    "anyin",
    "chdir",
    "cmd",
    "cmdrun",
    "cmdsudo",
    "command",
    "completions",
    "current_task_name",
    "dict_sort",
    "dmg",
    "effect",
    "elementadd",
    "elevate",
    "envsh",
    "exec_module_from_file",
    "filterm",
    "findfile",
    "findup",
    "firstfound",
    "flatten",
    "framesimple",
    "from_latin9",
    "fromiter",
    "getpths",
    "getsitedir",
    "group_user",
    "gz",
    "in_tox",
    "indict",
    "iscoro",
    "map_with_args",
    "mip",
    "noexc",
    "parent",
    "returncode",
    "sourcepath",
    "siteimported",
    "split_pairs",
    "stdout",
    "stdquiet",
    "suppress",
    "syssudo",
    "tardir",
    "tilde",
    "timestamp_now",
    "to_camel",
    "to_latin9",
    "tomodules",
    "urljson",
    "varname",
    "which",
    "yield_if",
    "yield_last",
)

import asyncio
import collections
import contextlib
import fnmatch
import getpass
import grp
import importlib.util
import inspect
import io
import json
import os
import pickle
import pwd
import re
import shutil
import subprocess
import sys
import sysconfig
import tarfile
import tempfile
import textwrap
import time
import types
import urllib.request
from collections.abc import Callable, Generator, Iterable, Iterator, MutableMapping
from typing import TYPE_CHECKING, Any, AnyStr, ParamSpec, TextIO, TypeVar, Union, cast

from nodeps.modules.constants import (
    EXECUTABLE,
    EXECUTABLE_SITE,
    GITHUB_TOKEN,
    MACOS,
    NODEPS_PROJECT_NAME,
    PW_ROOT,
    PW_USER,
    SUDO,
    USER,
)
from nodeps.modules.datas import GroupUser, IdName
from nodeps.modules.errors import CalledProcessError, CmdError, CommandNotFoundError
from nodeps.modules.path import AnyPath, FrameSimple, Path, toiter

if TYPE_CHECKING:
    from nodeps.modules.typings import ExcType, PathIsLiteral, RunningLoop

_KT = TypeVar("_KT")
_T = TypeVar("_T")
_VT = TypeVar("_VT")
P = ParamSpec("P")
T = TypeVar("T")


def aioclosed() -> bool:
    """Check if event loop is closed."""
    return asyncio.get_event_loop().is_closed()


async def aiocmd(*args, **kwargs) -> subprocess.CompletedProcess:
    """Async Exec Command.

    Examples:
        >>> import asyncio
        >>> from tempfile import TemporaryDirectory
        >>> from nodeps import Path, aiocmd
        >>> with TemporaryDirectory() as tmp:
        ...     tmp = Path(tmp)
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


async def aiodmg(src: AnyPath, dest: AnyPath) -> None:
    """Async Open dmg file and copy the app to dest.

    Examples:
        >>> from nodeps import aiodmg
        >>> async def test():    # doctest: +SKIP
        ...     await aiodmg("/tmp/JetBrains.dmg", "/tmp/JetBrains")

    Args:
        src: dmg file
        dest: path to copy to

    Returns:
        CompletedProcess
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        await aiocmd("hdiutil", "attach", "-mountpoint", tmpdir, "-nobrowse", "-quiet", src)
        for item in Path(src).iterdir():
            if item.name.endswith(".app"):
                await aiocmd("cp", "-r", Path(tmpdir) / item.name, dest)
                await aiocmd("xattr", "-r", "-d", "com.apple.quarantine", dest)
                await aiocmd("hdiutil", "detach", tmpdir, "-force")
                break


async def aiogz(src: AnyPath, dest: AnyPath = ".") -> Path:
    """Async ncompress .gz src to dest (default: current directory).

    It will be uncompressed to the same directory name as src basename.
    Uncompressed directory will be under dest directory.

    Examples:
        >>> import os
        >>> import tempfile
        >>> from nodeps import Path, aiogz, tardir
        >>>
        >>> cwd = Path.cwd()
        >>> with tempfile.TemporaryDirectory() as workdir:
        ...     os.chdir(workdir)
        ...     with tempfile.TemporaryDirectory() as compress:
        ...         file = Path(compress) / "test.txt"
        ...         _ = file.touch()
        ...         compressed = tardir(compress)
        ...         with tempfile.TemporaryDirectory() as uncompress:
        ...             uncompressed = asyncio.run(aiogz(compressed, uncompress))
        ...             assert uncompressed.is_dir()
        ...             assert Path(uncompressed).joinpath(file.name).exists()
        >>> os.chdir(cwd)

    Args:
        src: file to uncompress
        dest: destination directory to where uncompress directory will be created (default: current directory)

    Returns:
        Absolute Path of the Uncompressed Directory
    """
    return await asyncio.to_thread(gz, src, dest)


def aioloop() -> RunningLoop | None:
    """Get running loop."""
    return noexc(RuntimeError, asyncio.get_running_loop)


def aioloopid() -> int | None:
    """Get running loop id."""
    try:
        return asyncio.get_running_loop()._selector
    except RuntimeError:
        return None


def aiorunning() -> bool:
    """Check if event loop is running."""
    return asyncio.get_event_loop().is_running()


def allin(origin: Iterable, destination: Iterable) -> bool:
    """Checks all items in origin are in destination iterable.

    Examples:
        >>> from nodeps import allin
        >>> from nodeps.variables.builtin import BUILTIN_CLASS
        >>>
        >>> class Int(int):
        ...     pass
        >>> allin(tuple.__mro__, BUILTIN_CLASS)
        True
        >>> allin(Int.__mro__, BUILTIN_CLASS)
        False
        >>> allin('tuple int', 'bool dict int')
        False
        >>> allin('bool int', ['bool', 'dict', 'int'])
        True
        >>> allin(['bool', 'int'], ['bool', 'dict', 'int'])
        True

    Args:
        origin: origin iterable.
        destination: destination iterable to check if origin items are in.

    Returns:
        True if all items in origin are in destination.
    """
    origin = toiter(origin)
    destination = toiter(destination)
    return all(x in destination for x in origin)


def ami(user: str = "root") -> bool:
    """Check if Current User is User in Argument (default: root).

    Examples:
        >>> from nodeps import ami
        >>> from nodeps import USER
        >>> from nodeps import LOCAL
        >>> from nodeps import DOCKER
        >>> from nodeps import MACOS
        >>>
        >>> assert ami(USER) is True
        >>> if LOCAL and MACOS:
        ...     assert ami() is False
        >>> if DOCKER:
        ...     assert ami() is True

    Arguments:
        user: to check against current user (Default: root)

    Returns:
        bool True if I am user, False otherwise
    """
    return os.getuid() == pwd.getpwnam(user or getpass.getuser()).pw_uid


def anyin(origin: Iterable, destination: Iterable) -> Any | None:
    """Checks any item in origin are in destination iterable and return the first found.

    Examples:
        >>> from nodeps import anyin
        >>> from nodeps.variables.builtin import BUILTIN_CLASS
        >>>
        >>> class Int(int):
        ...     pass
        >>> anyin(tuple.__mro__, BUILTIN_CLASS)
        <class 'tuple'>
        >>> assert anyin('tuple int', BUILTIN_CLASS) is None
        >>> anyin('tuple int', 'bool dict int')
        'int'
        >>> anyin('tuple int', ['bool', 'dict', 'int'])
        'int'
        >>> anyin(['tuple', 'int'], ['bool', 'dict', 'int'])
        'int'

    Args:
        origin: origin iterable.
        destination: destination iterable to check if any of origin items are in.

    Returns:
        First found if any item in origin are in destination.
    """
    origin = toiter(origin)
    destination = toiter(destination)
    for item in toiter(origin):
        if item in destination:
            return item
    return None


@contextlib.contextmanager
def chdir(data: AnyPath | bool = True) -> Iterable[tuple[Path, Path]]:
    """Change directory and come back to previous directory.

    Examples:
        >>> from nodeps import Path
        >>> from nodeps import chdir
        >>> from nodeps import MACOS
        >>>
        >>> previous = Path.cwd()
        >>> new = Path('/usr')
        >>> with chdir(new) as (pr, ne):
        ...     assert previous == pr
        ...     assert new == ne
        ...     assert ne == Path.cwd()
        >>>
        >>> if MACOS:
        ...     new = Path('/bin/ls')
        ...     with chdir(new) as (pr, ne):
        ...         assert previous == pr
        ...         assert new.parent == ne
        ...         assert ne == Path.cwd()
        >>>
        >>> if MACOS:
        ...     new = Path('/bin/foo')
        ...     with chdir(new) as (pr, ne):
        ...         assert previous == pr
        ...         assert new.parent == ne
        ...         assert ne == Path.cwd()
        >>>
        >>> with chdir() as (pr, ne):
        ...     assert previous == pr
        ...     if MACOS:
        ...         assert "var" in str(ne)
        ...     assert ne == Path.cwd() # doctest: +SKIP

    Args:
        data: directory or parent if file or True for temp directory

    Returns:
        Old directory and new directory
    """

    def y(new):
        os.chdir(new)
        return oldpwd, new

    oldpwd = Path.cwd()
    try:
        if data is True:
            with tempfile.TemporaryDirectory() as tmp:
                yield y(Path(tmp))
        else:
            yield y(parent(data, none=False))
    finally:
        os.chdir(oldpwd)


def cmd(*args, **kwargs) -> subprocess.CompletedProcess:
    """Exec Command.

    Examples:
        >>> import tempfile
        >>> from nodeps import Path, cmd
        >>>
        >>> with tempfile.TemporaryDirectory() as tmp:
        ...     rv = cmd("git", "clone", "https://github.com/octocat/Hello-World.git", tmp)
        ...     assert rv.returncode == 0
        ...     assert (Path(tmp) / "README").exists()

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
    r"""Runs a cmd.

    Examples:
        >>> from nodeps import CI
        >>> from nodeps import cmdrun
        >>> from nodeps import in_tox
        >>>
        >>> cmdrun('ls a')  # doctest: +ELLIPSIS
        CompletedProcess(args='ls a', returncode=..., stdout=[], stderr=[...])
        >>> assert 'Requirement already satisfied' in cmdrun('pip install pip', py=True).stdout[0]
        >>> cmdrun('ls a', shell=False, lines=False)  # doctest: +ELLIPSIS
        CompletedProcess(args=['ls', 'a'], returncode=..., stdout='', stderr=...)
        >>> cmdrun('echo a', lines=False)  # Extra '\' added to avoid docstring error.
        CompletedProcess(args='echo a', returncode=0, stdout='a\n', stderr='')
        >>> assert "venv" not in cmdrun("sysconfig", py=True, lines=False).stdout
        >>> if os.environ.get("VIRTUAL_ENV"):
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
            return proc.stdout
        if lines:
            return proc.stderr.decode("utf-8").splitlines()
        return proc.stderr

    rv = subprocess.CompletedProcess(proc.args, proc.returncode, std(), std(False))
    if rv.returncode != 0 and exc:
        raise CmdError(rv)
    return rv


def cmdsudo(*args, user: str = "root", **kwargs) -> subprocess.CompletedProcess | None:
    """Run Program with sudo if user is different that the current user.

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
    """Exec Command with the following defaults compared to :func:`subprocess.run`.

        - capture_output=True
        - text=True
        - check=True

    Examples:
        >>> from nodeps import Path
        >>> import tempfile
        >>> with tempfile.TemporaryDirectory() as tmp:
        ...     rv = command("git", "clone", "https://github.com/octocat/Hello-World.git", tmp)
        ...     assert rv.returncode == 0
        ...     assert (Path(tmp) / ".git").exists()

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


def completions(name: str, install: bool = True, uninstall: bool = False) -> str | None:
    """Generate completions for command.

    Args:
        name: command name
        install: install completions to /usr/local/etc/bash_completion.d/ or /etc/bash_completion.d
        uninstall: uninstall completions

    Returns:
        Path to file if installed or prints if not installed
    """
    completion = f"""# shellcheck shell=bash

#
# generated by {__file__}

#######################################
# {name} completion
# Globals:
#   COMPREPLY
#   COMP_CWORD
#   COMP_WORDS
# Arguments:
#   1
# Returns:
#   0 ...
#######################################
_{name}_completion() {{
    local IFS=$'
'
  mapfile -t COMPREPLY < <(env COMP_WORDS="${{COMP_WORDS[*]}}" \\
    COMP_CWORD="${{COMP_CWORD}}" \\
    _{name.upper()}_COMPLETE=complete_bash "$1")
  return 0
}}

complete -o default -F _{name}_completion {name}
"""
    path = Path("/usr/local/etc/bash_completion.d" if MACOS else "/etc/bash_completion.d").mkdir()
    # if not MACOS and not os.access(path, os.W_OK, effective_ids=True):
    #     elevate()
    path.chown()
    file = Path(path, f"{NODEPS_PROJECT_NAME}:{name}.bash")
    if uninstall:
        file.unlink(missing_ok=True)
        return None
    if install:
        if not file.is_file():
            file.write_text(completion)
            return str(file)
        with Path.tempfile() as tmp:
            tmp.write_text(completion)
            if not tmp.cmp(file):
                shutil.move(tmp, file)
                return str(file)
        return None
    print(completion)
    return None


def current_task_name() -> str:
    """Current asyncio task name."""
    return asyncio.current_task().get_name() if aioloop() else ""


def dict_sort(
        data: dict[_KT, _VT], ordered: bool = False, reverse: bool = False
) -> dict[_KT, _VT] | collections.OrderedDict[_KT, _VT]:
    """Order a dict based on keys.

    Examples:
        >>> import platform
        >>> from collections import OrderedDict
        >>> from nodeps import dict_sort
        >>>
        >>> d = {"b": 2, "a": 1, "c": 3}
        >>> dict_sort(d)
        {'a': 1, 'b': 2, 'c': 3}
        >>> dict_sort(d, reverse=True)
        {'c': 3, 'b': 2, 'a': 1}
        >>> v = platform.python_version()
        >>> if "rc" not in v:
        ...     # noinspection PyTypeHints
        ...     assert dict_sort(d, ordered=True) == OrderedDict([('a', 1), ('b', 2), ('c', 3)])

    Args:
        data: dict to be ordered.
        ordered: OrderedDict.
        reverse: reverse.

    Returns:
        Union[dict, collections.OrderedDict]: Dict sorted
    """
    data = {key: data[key] for key in sorted(data.keys(), reverse=reverse)}
    if ordered:
        return collections.OrderedDict(data)
    return data


def dmg(src: AnyPath, dest: AnyPath) -> None:
    """Open dmg file and copy the app to dest.

    Examples:
        >>> from nodeps import dmg
        >>> dmg("/tmp/JetBrains.dmg", "/tmp/JetBrains")  # doctest: +SKIP

    Args:
        src: dmg file
        dest: path to copy to

    Returns:
        CompletedProcess
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        cmd("hdiutil", "attach", "-mountpoint", tmpdir, "-nobrowse", "-quiet", src)
        for item in Path(src).iterdir():
            if item.name.endswith(".app"):
                cmd("cp", "-r", Path(tmpdir) / item.name, dest)
                cmd("xattr", "-r", "-d", "com.apple.quarantine", dest)
                cmd("hdiutil", "detach", tmpdir, "-force")
                break


def effect(apply: Callable, *args: Iterable) -> None:
    """Perform function on iterable.

    Examples:
        >>> from types import SimpleNamespace
        >>> from nodeps import effect
        >>> simple = SimpleNamespace()
        >>> effect(lambda x: simple.__setattr__(x, dict()), 'a b', 'c')
        >>> assert simple.a == {}
        >>> assert simple.b == {}
        >>> assert simple.c == {}

    Args:
        apply: Function to apply.
        *args: Iterable to perform function.

    Returns:
        No Return.
    """
    for arg in toiter(args):
        for item in arg:
            apply(item)


def elementadd(name: str | tuple[str, ...], closing: bool | None = False) -> str:
    """Converts to HTML element.

    Examples:
        >>> from nodeps import elementadd
        >>>
        >>> assert elementadd('light-black') == '<light-black>'
        >>> assert elementadd('light-black', closing=True) == '</light-black>'
        >>> assert elementadd(('green', 'bold',)) == '<green><bold>'
        >>> assert elementadd(('green', 'bold',), closing=True) == '</green></bold>'

    Args:
        name: text or iterable text.
        closing: True if closing/end, False if opening/start.

    Returns:
        Str
    """
    return "".join(f'<{"/" if closing else ""}{i}>' for i in ((name,) if isinstance(name, str) else name))


def elevate():
    """Other https://github.com/netinvent/command_runner/blob/master/command_runner/elevate.py."""
    if os.getuid() == 0 or not SUDO:
        return

    os.execv(SUDO, sys.argv)  # noqa: S606
    # subprocess.check_call(SUDO, *sys.argv)


def envsh(
        path: AnyPath = ".env",
        missing_ok: bool = False,
        override: bool = True,
) -> dict[str, str]:
    """Source ``path`` or ``path``relative to cwd upwards and return the resulting environment as a dictionary.

    Args:
        path: bash file to source or name relative to cwd upwards.
        missing_ok: do not raise exception if file ot found.
        override: override os.environ.

    Raises:
        FileNotFoundError.

    Return:
        Dict with updated values
    """
    p = Path(path)
    p = p.find_up()
    if p is None:
        if missing_ok:
            return {}
        msg = f"{path=}"
        raise FileNotFoundError(msg)

    with Path.tempfile() as tmp:
        code = f"import os, pickle; pickle.dump(dict(os.environ), open('{tmp}', 'wb'))"
        subprocess.check_call(
            f'set -a && . {p} && {sys.executable} -c "{code}"',
            shell=True,
        )
        with tmp.open("rb") as f:
            environ = pickle.load(f)  # noqa: S301

    updated = {
        key: value
        for key, value in environ.items()
        if os.environ.get(key) != value and key not in ["PWD", "SHLVL", "_", "__CF_USER_TEXT_ENCODING", "LC_CTYPE"]
    }
    if override:
        os.environ.update(updated)

    return updated


def exec_module_from_file(file: Path | str, name: str | None = None) -> types.ModuleType:
    """Executes module from file location.

    Examples:
        >>> import nodeps
        >>> from nodeps import exec_module_from_file
        >>> m = exec_module_from_file(nodeps.__file__)
        >>> assert m.__name__ == nodeps.__name__

    Args:
        file: file location
        name: module name (default from file)

    Returns:
        Module instance
    """
    file = Path(file)
    spec = importlib.util.spec_from_file_location(
        name or file.parent.name if file.name == "__init__.py" else file.stem, file
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def filterm(
        d: MutableMapping[_KT, _VT], k: Callable[..., bool] = lambda x: True, v: Callable[..., bool] = lambda x: True
) -> MutableMapping[_KT, _VT]:
    """Filter Mutable Mapping.

    Examples:
        >>> from nodeps import filterm
        >>>
        >>> assert filterm({'d':1}) == {'d': 1}
        >>> # noinspection PyUnresolvedReferences
        >>> assert filterm({'d':1}, lambda x: x.startswith('_')) == {}
        >>> # noinspection PyUnresolvedReferences
        >>> assert filterm({'d': 1, '_a': 2}, lambda x: x.startswith('_'), lambda x: isinstance(x, int)) == {'_a': 2}

    Returns:
        Filtered dict with
    """
    # noinspection PyArgumentList
    return d.__class__({x: y for x, y in d.items() if k(x) and v(y)})


def findfile(pattern, path: AnyPath = None) -> list[Path]:
    """Find file with pattern.

    Examples:
        >>> from pathlib import Path
        >>> import nodeps
        >>> from nodeps import findfile, MACOS, LOCAL
        >>>
        >>> if MACOS and LOCAL:
        ...     assert Path(nodeps.__file__) in findfile("*.py")

    Args:
        pattern: pattern to search files
        path: default cwd

    Returns:
        list of files found
    """
    result = []
    for root, _, files in os.walk(path or Path.cwd()):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                result.append(Path(root, name))
    return result


def findup(
        path: AnyPath = None,
        kind: PathIsLiteral = "is_file",
        name: str | Path = ".env",
        uppermost: bool = False,
) -> Path | None:
    """Find up if name exists or is file or directory.

    Examples:
        >>> import email
        >>> import email.mime
        >>> import nodeps
        >>> from nodeps import chdir, findup, parent, Path, Env
        >>>
        >>>
        >>> file = Path(email.mime.__file__)
        >>>
        >>> env = Env()
        >>> input_file = env.GITHUB_WORKSPACE if env.GITHUB_WORKSPACE else nodeps.__file__
        >>> with chdir(parent(input_file)):
        ...     pyproject_toml = findup(input_file, name="pyproject.toml")
        ...     assert pyproject_toml.is_file()
        >>>
        >>> with chdir(parent(email.mime.__file__)):
        ...     email_mime_py = findup(name="__init__.py")
        ...     assert email_mime_py.is_file()
        ...     assert email_mime_py == Path(email.mime.__file__)
        ...     email_py = findup(name="__init__.py", uppermost=True)
        ...     assert email_py.is_file()
        ...     assert email_py == Path(email.__file__)
        >>>
        >>> assert findup(file, kind="exists", name="__init__.py") == file.parent / "__init__.py"
        >>> assert findup(file, name="__init__.py") == file.parent / "__init__.py"
        >>> assert findup(file, name="__init__.py", uppermost=True) == file.parent.parent / "__init__.py"

    Args:
        path: CWD if None or Path.
        kind: Exists, file or directory.
        name: File or directory name.
        uppermost: Find uppermost found if True (return the latest found if more than one) or first if False.

    Returns:
        Path if found.
    """
    name = name.name if isinstance(name, Path) else name
    start = parent(path or Path.cwd())
    latest = None
    while True:
        if getattr(find := start / name, kind)():
            if not uppermost:
                return find
            latest = find
        if (start := start.parent) == Path("/"):
            return latest


def firstfound(data: Iterable, apply: Callable) -> Any:
    """Returns first value in data if apply is True.

    Examples:
        >>> from nodeps import firstfound
        >>>
        >>> assert firstfound([1, 2, 3], lambda x: x == 2) == 2
        >>> assert firstfound([1, 2, 3], lambda x: x == 4) is None

    Args:
        data: iterable.
        apply: function to apply.

    Returns:
        Value if found.
    """
    for i in data:
        if apply(i):
            return i
    return None


def flatten(
        data: tuple | list | set,
        recurse: bool = False,
        unique: bool = False,
        sort: bool = True,
) -> tuple | list | set:
    """Flattens an Iterable.

    Examples:
        >>> from nodeps import flatten
        >>>
        >>> assert flatten([1, 2, 3, [1, 5, 7, [2, 4, 1, ], 7, 6, ]]) == [1, 2, 3, 1, 5, 7, [2, 4, 1], 7, 6]
        >>> assert flatten([1, 2, 3, [1, 5, 7, [2, 4, 1, ], 7, 6, ]], recurse=True) == [1, 1, 1, 2, 2, 3, 4, 5, 6, 7, 7]
        >>> assert flatten((1, 2, 3, [1, 5, 7, [2, 4, 1, ], 7, 6, ]), unique=True) == (1, 2, 3, 4, 5, 6, 7)

    Args:
        data: iterable
        recurse: recurse
        unique: when recurse
        sort: sort

    Returns:
        Union[list, Iterable]:
    """
    if unique:
        recurse = True

    cls = data.__class__

    flat = []
    _ = [
        flat.extend(flatten(item, recurse, unique) if recurse else item)
        if isinstance(item, list)
        else flat.append(item)
        for item in data
        if item
    ]
    value = set(flat) if unique else flat
    if sort:
        try:
            value = cls(sorted(value))
        except TypeError:
            value = cls(value)
    return value


def framesimple(data: inspect.FrameInfo | types.FrameType | types.TracebackType) -> FrameSimple | None:
    """Returns :class:`nodeps.FrameSimple`.

    Examples:
        >>> import inspect
        >>> from nodeps import Path
        >>> from nodeps import framesimple
        >>>
        >>> frameinfo = inspect.stack()[0]
        >>> finfo = framesimple(frameinfo)
        >>> ftype = framesimple(frameinfo.frame)
        >>> assert frameinfo.frame.f_code == finfo.code
        >>> assert frameinfo.frame == finfo.frame
        >>> assert frameinfo.filename == str(finfo.path)
        >>> assert frameinfo.lineno == finfo.lineno

    Returns:
        :class:`FrameSimple`.
    """
    if isinstance(data, inspect.FrameInfo):
        frame = data.frame
        back = frame.f_back
        lineno = data.lineno
    elif isinstance(data, types.FrameType):
        frame = data
        back = data.f_back
        lineno = data.f_lineno
    elif isinstance(data, types.TracebackType):
        frame = data.tb_frame
        back = data.tb_next
        lineno = data.tb_lineno
    else:
        return None

    code = frame.f_code
    f_globals = frame.f_globals
    f_locals = frame.f_locals
    function = code.co_name
    v = f_globals | f_locals
    name = v.get("__name__") or function
    return FrameSimple(
        back=back,
        code=code,
        frame=frame,
        function=function,
        globals=f_globals,
        lineno=lineno,
        locals=f_locals,
        name=name,
        package=v.get("__package__") or name.split(".")[0],
        path=sourcepath(data),
        vars=v,
    )


def from_latin9(*args) -> str:
    """Converts string from latin9 hex.

    Examples:
        >>> from nodeps import from_latin9
        >>>
        >>> from_latin9("f1")
        'ñ'
        >>>
        >>> from_latin9("4a6f73e920416e746f6e696f205075e972746f6c6173204d6f6e7461f1e973")
        'José Antonio Puértolas Montañés'
        >>>
        >>> from_latin9("f1", "6f")
        'ño'

    Args:
        args: strings to convert to latin9

    Returns:
        str
    """
    rv = ""
    if len(args) == 1:
        pairs = split_pairs(args[0])
        for pair in pairs:
            rv += bytes.fromhex("".join(pair)).decode("latin9")
    else:
        for char in args:
            rv += bytes.fromhex(char).decode("latin9")
    return rv


def fromiter(data, *args):
    """Gets attributes from Iterable of objects and returns dict with.

    Examples:
        >>> from types import SimpleNamespace as Simple
        >>> from nodeps import fromiter
        >>>
        >>> assert fromiter([Simple(a=1), Simple(b=1), Simple(a=2)], 'a', 'b', 'c') == {'a': [1, 2], 'b': [1]}
        >>> assert fromiter([Simple(a=1), Simple(b=1), Simple(a=2)], ('a', 'b', ), 'c') == {'a': [1, 2], 'b': [1]}
        >>> assert fromiter([Simple(a=1), Simple(b=1), Simple(a=2)], 'a b c') == {'a': [1, 2], 'b': [1]}

    Args:
        data: object.
        *args: attributes.

    Returns:
        Tuple
    """
    value = {k: [getattr(C, k) for C in data if hasattr(C, k)] for i in args for k in toiter(i)}
    return {k: v for k, v in value.items() if v}


def getpths() -> dict[str, Path] | None:
    """Get list of pths under ``sitedir``.

    Examples:
        >>> from nodeps import getpths
        >>>
        >>> pths = getpths()
        >>> assert "distutils-precedence" in pths

    Returns:
        Dictionary with pth name and file
    """
    try:
        s = getsitedir()
        names = os.listdir(s)
    except OSError:
        return None
    return {re.sub("(-[0-9].*|.pth)", "", name): Path(s / name) for name in names if name.endswith(".pth")}


def getsitedir(index: bool = 2) -> Path:
    """Get site directory from stack if imported by :mod:`site` in a ``.pth`` file or :mod:`sysconfig`.

    Examples:
        >>> from nodeps import getsitedir
        >>> assert "packages" in str(getsitedir())

    Args:
        index: 1 if directly needed by this function (default: 2), for caller to this function

    Returns:
        Path instance with site directory
    """
    if (s := sys._getframe(index).f_locals.get("sitedir")) is None:
        s = sysconfig.get_paths()["purelib"]
    return Path(s)


def group_user(data: int | str = USER) -> GroupUser:
    """Group and User for Name (id if name is str and vice versa).

    Examples:
        >>> import os
        >>> import pathlib
        >>>
        >>> from nodeps import group_user
        >>> from nodeps import PW_USER, PW_ROOT, MACOS, LOCAL
        >>>
        >>> stat = pathlib.Path().stat()
        >>> gu = group_user()
        >>> assert gu.group.id == stat.st_gid and gu.user.id == stat.st_uid
        >>> gu = group_user(data=PW_USER.pw_uid)
        >>> actual_gname = gu.group.name
        >>> assert gu.user.name == PW_USER.pw_name
        >>> gu = group_user('root')
        >>> if MACOS and LOCAL:
        ...     assert gu.group.id != stat.st_gid and gu.user.id == 0
        >>> gu = group_user(data=0)
        >>> if MACOS and LOCAL:
        ...     assert gu.group.name != actual_gname and gu.user.name == 'root'

    Args:
        data: usename or id (default: USER)

    Returns:
        GroupUser.
    """
    if isinstance(data, str):
        struct = struct if data == (struct := PW_USER).pw_name or data == (struct := PW_ROOT).pw_name \
            else pwd.getpwnam(data)  # noqa: PLR1714
    else:
        struct = struct if data == (struct := PW_USER).pw_uid or data == (struct := PW_ROOT).pw_uid \
            else pwd.getpwuid(data)  # noqa: PLR1714
    group = IdName(id=struct.pw_gid, name=grp.getgrgid(struct.pw_gid).gr_name)
    user = IdName(id=struct.pw_uid, name=struct.pw_name)
    return GroupUser(group=group, user=user)


def gz(src: AnyPath, dest: AnyPath = ".") -> Path:
    """Uncompress .gz src to dest (default: current directory).

    It will be uncompressed to the same directory name as src basename.
    Uncompressed directory will be under dest directory.

    Examples:
        >>> import os
        >>> import tempfile
        >>> from nodeps import Path, gz, tardir
        >>> cwd = Path.cwd()
        >>> with tempfile.TemporaryDirectory() as workdir:
        ...     os.chdir(workdir)
        ...     with tempfile.TemporaryDirectory() as compress:
        ...         file = Path(compress) / "test.txt"
        ...         _ = file.touch()
        ...         compressed = tardir(compress)
        ...         with tempfile.TemporaryDirectory() as uncompress:
        ...             uncompressed = gz(compressed, uncompress)
        ...             assert uncompressed.is_dir()
        ...             assert Path(uncompressed).joinpath(file.name).exists()
        >>> os.chdir(cwd)

    Args:
        src: file to uncompress
        dest: destination directory to where uncompress directory will be created (default: current directory)

    Returns:
        Absolute Path of the Uncompressed Directory
    """
    dest = Path(dest)
    with tarfile.open(src, "r:gz") as tar:
        tar.extractall(dest)
        return (dest / tar.getmembers()[0].name).parent.absolute()


def in_tox() -> bool:
    """Running in tox."""
    return ".tox" in sysconfig.get_paths()["purelib"]


def indict(data: MutableMapping, items: MutableMapping | None = None, **kwargs: Any) -> bool:
    """All item/kwargs pairs in flat dict.

    Examples:
        >>> from nodeps import indict
        >>> from nodeps.variables.builtin import BUILTIN
        >>>
        >>> assert indict(BUILTIN, {'iter': iter}, credits=credits) is True
        >>> assert indict(BUILTIN, {'iter': 'fake'}) is False
        >>> assert indict(BUILTIN, {'iter': iter}, credits='fake') is False
        >>> assert indict(BUILTIN, credits='fake') is False

    Args:
        data: dict to search.
        items: key/value pairs.
        **kwargs: key/value pairs.

    Returns:
        True if all pairs in dict.
    """
    return all(x[0] in data and x[1] == data[x[0]] for x in ((items if items else {}) | kwargs).items())


def iscoro(data: Any) -> bool:
    """Is coro?."""
    return any(
        [
            inspect.isasyncgen(data),
            inspect.isasyncgenfunction(data),
            asyncio.iscoroutine(data),
            inspect.iscoroutinefunction(data),
        ]
    )


def map_with_args(
        data: Any, func: Callable, /, *args, pred: Callable = lambda x: bool(x), split: str = " ", **kwargs
) -> list:
    """Apply pred/filter to data and map with args and kwargs.

    Examples:
        >>> from nodeps import map_with_args
        >>>
        >>> # noinspection PyUnresolvedReferences
        >>> def f(i, *ar, **kw):
        ...     return f'{i}: {[a(i) for a in ar]}, {", ".join([f"{k}: {v(i)}" for k, v in kw.items()])}'
        >>> map_with_args('0.1.2', f, int, list, pred=lambda x: x != '0', split='.', int=int, str=str)
        ["1: [1, ['1']], int: 1, str: 1", "2: [2, ['2']], int: 2, str: 2"]

    Args:
        data: data.
        func: final function to map.
        *args: args to final map function.
        pred: pred to filter data before map.
        split: split for data str.
        **kwargs: kwargs to final map function.

    Returns:
        List with results.
    """
    return [func(item, *args, **kwargs) for item in yield_if(data, pred=pred, split=split)]


def mip() -> str | None:
    """My Public IP.

    Examples:
        >>> from nodeps import mip
        >>>
        >>> mip()  # doctest: +ELLIPSIS
        '...............'
    """
    return urllib.request.urlopen("https://checkip.amazonaws.com", timeout=5).read().strip().decode()  # noqa: S310


def noexc(
        func: Callable[..., _T], *args: Any, default_: Any = None, exc_: ExcType = Exception, **kwargs: Any
) -> _T | Any:
    """Execute function suppressing exceptions.

    Examples:
        >>> from nodeps import noexc
        >>> assert noexc(dict(a=1).pop, 'b', default_=2, exc_=KeyError) == 2

    Args:
        func: callable.
        *args: args.
        default_: default value if exception is raised.
        exc_: exception or exceptions.
        **kwargs: kwargs.

    Returns:
        Any: Function return.
    """
    try:
        return func(*args, **kwargs)
    except exc_:
        return default_


def parent(path: AnyPath = __file__, none: bool = True) -> Path | None:
    """Parent if File or None if it does not exist.

    Examples:
        >>> from nodeps import parent
        >>>
        >>> parent("/bin/ls")
        Path('/bin')
        >>> parent("/bin")
        Path('/bin')
        >>> parent("/bin/foo", none=False)
        Path('/bin')
        >>> parent("/bin/foo")

    Args:
        path: file or dir.
        none: return None if it is not a directory and does not exist (default: True)

    Returns:
        Path
    """
    return path.parent if (path := Path(path)).is_file() else path if path.is_dir() else None if none else path.parent


def returncode(c: str | list[str], shell: bool = True) -> int:
    """Runs command in shell and returns returncode showing stdout and stderr.

    No exception is raised

    Examples:
        >>> from nodeps import returncode
        >>>
        >>> assert returncode("ls /bin/ls") == 0
        >>> assert returncode("ls foo") in  [1, 2]

    Arguments:
        c: command to run
        shell: run in shell (default: True)

    Returns:
        return code

    """
    return subprocess.call(c, shell=shell)


def sourcepath(data: Any) -> Path:
    """Get path of object.

    Examples:
        >>> import asyncio
        >>> from nodeps import Path
        >>> from nodeps import sourcepath
        >>>
        >>> finfo = inspect.stack()[0]
        >>> globs_locs = (finfo.frame.f_globals | finfo.frame.f_locals).copy()
        >>> assert sourcepath(sourcepath) == Path(__file__)
        >>> assert sourcepath(asyncio.__file__) == Path(asyncio.__file__)
        >>> assert sourcepath(dict(a=1)) == Path("{'a': 1}")

    Returns:
        Path.
    """
    if isinstance(data, MutableMapping):
        f = data.get("__file__")
    elif isinstance(data, inspect.FrameInfo):
        f = data.filename
    else:
        try:
            f = inspect.getsourcefile(data) or inspect.getfile(data)
        except TypeError:
            f = None
    return Path(f or str(data))


def siteimported() -> str | None:
    """True if imported by :mod:`site` in a ``.pth`` file."""
    s = None
    _frame = sys._getframe()
    while _frame and (s := _frame.f_locals.get("sitedir")) is None:
        _frame = _frame.f_back
    return s


def split_pairs(text):
    """Split text in pairs for even length.

    Examples:
        >>> from nodeps import split_pairs
        >>>
        >>> split_pairs("123456")
        [('1', '2'), ('3', '4'), ('5', '6')]

    Args:
        text: text to split in pairs

    Returns:
        text
    """
    return list(zip(text[0::2], text[1::2], strict=True))


def stdout(
        shell: AnyStr, keepends: bool = False, split: bool = False, cwd: Path | str | None = None
) -> list[str] | str | None:
    """Return stdout of executing cmd in a shell or None if error.

    Execute the string 'cmd' in a shell with 'subprocess.getstatusoutput' and
    return a stdout if success. The locale encoding is used
    to decode the output and process newlines.

    A trailing newline is stripped from the output.

    Examples:
        >>> from nodeps import stdout
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
        cwd: cwd

    Returns:
        Stdout or None if error.
    """
    with Path(cwd or "").cd():
        exitcode, data = subprocess.getstatusoutput(shell)

    if exitcode == 0:
        if split:
            return data.splitlines(keepends=keepends)
        return data
    return None


@contextlib.contextmanager
def stdquiet() -> tuple[TextIO, TextIO]:
    """Redirect stdout/stderr to StringIO objects to prevent console output from distutils commands.

    Returns:
        Stdout, Stderr
    """
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    new_stdout = sys.stdout = io.StringIO()
    new_stderr = sys.stderr = io.StringIO()
    try:
        yield new_stdout, new_stderr
    finally:
        new_stdout.seek(0)
        new_stderr.seek(0)
        sys.stdout = old_stdout
        sys.stderr = old_stderr


def suppress(
        func: Callable[P, T],
        *args: P.args,
        exception: ExcType | None = Exception,
        **kwargs: P.kwargs,
) -> T:
    """Try and supress exception.

    Args:
        func: function to call
        *args: args to pass to func
        exception: exception to suppress (default: Exception)
        **kwargs: kwargs to pass to func

    Returns:
        result of func
    """
    with contextlib.suppress(exception or Exception):
        return func(*args, **kwargs)


def syssudo(user: str = "root") -> subprocess.CompletedProcess | None:
    """Rerun Program with sudo ``sys.executable`` and ``sys.argv`` if user is different that the current user.

    Arguments:
        user: run as user (Default: False)

    Returns:
        CompletedProcess if the current user is not the same as user, None otherwise
    """
    if not ami(user):
        return cmd(["sudo", "-u", user, sys.executable, *sys.argv])
    return None


def tardir(src: AnyPath) -> Path:
    """Compress directory src to <basename src>.tar.gz in cwd.

    Examples:
        >>> import os
        >>> import tempfile
        >>> from nodeps import Path, tardir
        >>> cwd = Path.cwd()
        >>> with tempfile.TemporaryDirectory() as workdir:
        ...     os.chdir(workdir)
        ...     with tempfile.TemporaryDirectory() as compress:
        ...         file = Path(compress) / "test.txt"
        ...         _ = file.touch()
        ...         compressed = tardir(compress)
        ...         with tempfile.TemporaryDirectory() as uncompress:
        ...             uncompressed = gz(compressed, uncompress)
        ...             assert uncompressed.is_dir()
        ...             assert Path(uncompressed).joinpath(file.name).exists()
        >>> os.chdir(cwd)

    Args:
        src: directory to compress

    Raises:
        FileNotFoundError: No such file or directory
        ValueError: Can't compress current working directory

    Returns:
        Compressed Absolute File Path
    """
    src = Path(src)
    if not src.exists():
        msg = f"{src}: No such file or directory"
        raise FileNotFoundError(msg)

    if src.resolve() == Path.cwd().resolve():
        msg = f"{src}: Can't compress current working directory"
        raise ValueError(msg)

    name = Path(src).name + ".tar.gz"
    dest = Path(name)
    with tarfile.open(dest, "w:gz") as tar:
        for root, _, files in os.walk(src):
            for file_name in files:
                tar.add(Path(root, file_name))
        return dest.absolute()


def tilde(path: AnyPath = ".") -> str:
    """Replaces $HOME with ~.

    Examples:
        >>> from nodeps import Path, tilde
        >>> assert tilde(f"{Path.home()}/file") == f"~/file"

    Arguments:
        path: path to replace (default: '.')

    Returns:
        str
    """
    return str(path).replace(str(Path.home()), "~")


def timestamp_now(file: Path | str):
    """Set modified and create date of file to now."""
    now = time.time()
    os.utime(file, (now, now))


def to_camel(text: str, replace: bool = True) -> str:
    """Convert to Camel.

    Examples:
        >>> to_camel("__ignore_attr__")
        'IgnoreAttr'
        >>> to_camel("__ignore_attr__", replace=False)  # doctest: +SKIP
        '__Ignore_Attr__'

    Args:
        text: text to convert.
        replace: remove '_'  (default: True)

    Returns:
        Camel text.
    """
    rv = "".join(map(str.title, toiter(text, split="_")))
    return rv.replace("_", "") if replace else rv


def to_latin9(chars: str) -> str:
    """Converts string to latin9 hex.

    Examples:
        >>> from nodeps import AUTHOR
        >>> from nodeps import to_latin9
        >>>
        >>> to_latin9("ñ")
        'f1'
        >>>
        >>> to_latin9(AUTHOR)
        '4a6f73e920416e746f6e696f205075e972746f6c6173204d6f6e7461f1e973'

    Args:
        chars: chars to converto to latin9

    Returns:
        hex str
    """
    rv = ""
    for char in chars:
        rv += char.encode("latin9").hex()
    return rv


def tomodules(obj: Any, suffix: bool = True) -> str:
    """Converts Iterable to A.B.C.

    Examples:
        >>> from nodeps import tomodules
        >>> assert tomodules('a b c') == 'a.b.c'
        >>> assert tomodules('a b c.py') == 'a.b.c'
        >>> assert tomodules('a/b/c.py') == 'a.b.c'
        >>> assert tomodules(['a', 'b', 'c.py']) == 'a.b.c'
        >>> assert tomodules('a/b/c.py', suffix=False) == 'a.b.c.py'
        >>> assert tomodules(['a', 'b', 'c.py'], suffix=False) == 'a.b.c.py'

    Args:
        obj: iterable.
        suffix: remove suffix.

    Returns:
        String A.B.C
    """
    split = "/" if isinstance(obj, str) and "/" in obj else " "
    return ".".join(i.removesuffix(Path(i).suffix if suffix else "") for i in toiter(obj, split=split))


def urljson(
        data: str,
        rm: bool = False,
) -> dict:
    """Url open json.

    Examples:
        >>> import os
        >>> from nodeps import urljson
        >>> from nodeps import GIT
        >>> from nodeps import GITHUB_TOKEN
        >>> from nodeps import NODEPS_PROJECT_NAME
        >>>
        >>> if os.environ.get('GITHUB_TOKEN'):
        ...     github = urljson(f"https://api.github.com/repos/{GIT}/{NODEPS_PROJECT_NAME}")
        ...     assert github['name'] == NODEPS_PROJECT_NAME
        >>>
        >>> pypi = urljson(f"https://pypi.org/pypi/{NODEPS_PROJECT_NAME}/json")
        >>> assert pypi['info']['name'] == NODEPS_PROJECT_NAME

    Args:
        data: url
        rm: use pickle cache or remove it before

    Returns:
        dict:
    """
    if not rm and (rv := Path.pickle(name=data)):
        return rv

    if data.lower().startswith("https"):
        request = urllib.request.Request(data)
    else:
        msg = f"Non-HTTPS URL: {data}"
        raise ValueError(msg)
    if "github" in data:
        request.add_header("Authorization", f"token {GITHUB_TOKEN}")

    with urllib.request.urlopen(request) as response:  # noqa: S310
        return Path.pickle(name=data, data=json.loads(response.read().decode()), rm=rm)


def varname(index=2, lower=True, prefix=None, sep="_"):
    """Caller var name.

    Examples:
        >>> from dataclasses import dataclass
        >>> from nodeps import varname
        >>>
        >>> def function() -> str:
        ...     return varname()
        >>>
        >>> class ClassTest:
        ...     def __init__(self):
        ...         self.name = varname()
        ...
        ...     @property
        ...     def prop(self):
        ...         return varname()
        ...
        ...     # noinspection PyMethodMayBeStatic
        ...     def method(self):
        ...         return varname()
        >>>
        >>> @dataclass
        ... class DataClassTest:
        ...     def __post_init__(self):
        ...         self.name = varname()
        >>>
        >>> name = varname(1)
        >>> Function = function()
        >>> classtest = ClassTest()
        >>> method = classtest.method()
        >>> prop = classtest.prop
        >>> dataclasstest = DataClassTest()
        >>>
        >>> def test_var():
        ...     assert name == 'name'
        >>>
        >>> def test_function():
        ...     assert Function == function.__name__.lower()
        >>>
        >>> def test_class():
        ...     assert classtest.name == ClassTest.__name__.lower()
        >>>
        >>> def test_method():
        ...     assert classtest.method() == ClassTest.__name__.lower()
        ...     assert method == 'method'
        >>> def test_property():
        ...     assert classtest.prop == ClassTest.__name__.lower()
        ...     assert prop == 'prop'
        >>> def test_dataclass():
        ...     assert dataclasstest.name == DataClassTest.__name__.lower()

        .. code-block:: python

            class A:

                def __init__(self):

                    self.instance = varname()

            a = A()

            var = varname(1)

    Args:
        index: index.
        lower: lower.
        prefix: prefix to add.
        sep: split.

    Returns:
        Optional[str]: Var name.
    """
    with contextlib.suppress(IndexError, KeyError):
        _stack = inspect.stack()
        f = _stack[index - 1].function
        index = index + 1 if f == "__post_init__" else index
        if (line := textwrap.dedent(_stack[index].code_context[0])) and (
                var := re.sub(f"(.| ){f}.*", "", line.split(" = ")[0].replace("assert ", "").split(" ")[0])
        ):
            return (prefix if prefix else "") + (var.lower() if lower else var).split(sep=sep)[0]
    return None


def which(data="sudo", raises: bool = False) -> str:
    """Checks if cmd or path is executable.

    Examples:
        >>> from nodeps import which
        >>> if which():
        ...    assert "sudo" in which()
        >>> assert which('/bin/ls') == '/bin/ls'
        >>> which("foo", raises=True) # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
        nodeps.modules.errors.CommandNotFoundError: foo

    Attribute:
        data: command or path.
        raises: raise exception if command not found

    Raises:
        CommandNotFound:

    Returns:
        Cmd path or ""
    """
    rv = shutil.which(data, mode=os.X_OK) or ""

    if raises and not rv:
        raise CommandNotFoundError(data)
    return rv


def yield_if(
        data: Any,
        pred: Callable = lambda x: bool(x),
        split: str = " ",
        apply: Union[Callable, tuple[Callable, ...]] | None = None,  # noqa: UP007
) -> Generator:
    """Yield value if condition is met and apply function if predicate.

    Examples:
        >>> from nodeps import yield_if
        >>>
        >>> assert list(yield_if([True, None])) == [True]
        >>> assert list(yield_if('test1.test2', pred=lambda x: x.endswith('2'), split='.')) == ['test2']
        >>> assert list(yield_if('test1.test2', pred=lambda x: x.endswith('2'), split='.', \
        apply=lambda x: x.removeprefix('test'))) == ['2']
        >>> assert list(yield_if('test1.test2', pred=lambda x: x.endswith('2'), split='.', \
        apply=(lambda x: x.removeprefix('test'), lambda x: int(x)))) == [2]


    Args:
        data: data
        pred: predicate (default: if value)
        split: split char for str.
        apply: functions to apply if predicate is met.

    Returns:
        Yield values if condition is met and apply functions if provided.
    """
    for item in toiter(data, split=split):
        if pred(item):
            if apply:
                for func in toiter(apply):
                    item = func(item)  # noqa: PLW2901
            yield item


def yield_last(data: Any, split: str = " ") -> Iterator[tuple[bool, Any, None]]:
    """Yield value if condition is met and apply function if predicate.

    Examples:
        >>> from nodeps import yield_last
        >>>
        >>> assert list(yield_last([True, None])) == [(False, True, None), (True, None, None)]
        >>> assert list(yield_last('first last')) == [(False, 'first', None), (True, 'last', None)]
        >>> assert list(yield_last('first.last', split='.')) == [(False, 'first', None), (True, 'last', None)]
        >>> assert list(yield_last(dict(first=1, last=2))) == [(False, 'first', 1), (True, 'last', 2)]


    Args:
        data: data.
        split: split char for str.

    Returns:
        Yield value and True when is the last item on iterable
    """
    data = toiter(data, split=split)
    mm = isinstance(data, MutableMapping)
    total = len(data)
    count = 0
    for i in data:
        count += 1
        yield (
            count == total,
            *(
                i,
                data.get(i) if mm else None,
            ),
        )
