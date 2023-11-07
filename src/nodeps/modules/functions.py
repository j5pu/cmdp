"""Functions Module."""
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
    "current_task_name",
    "dict_sort",
    "dmg",
    "effect",
    "elementadd",
    "gz",
    "in_tox",
    "indict",
    "noexc",
    "parent",
    "tardir",
    "tilde",
    "which",
)

import asyncio
import collections
import contextlib
import getpass
import os
import pwd
import shutil
import subprocess
import sysconfig
import tarfile
import tempfile
from collections.abc import Callable, Iterable, MutableMapping
from typing import Any, TypeVar, cast

from .constants import EXECUTABLE, EXECUTABLE_SITE
from .errors import CalledProcessError, CmdError, CommandNotFoundError
from .path import AnyPath, Path, toiter
from .typings import ExcType, RunningLoop

_KT = TypeVar("_KT")
_T = TypeVar("_T")
_VT = TypeVar("_VT")


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
    return path.parent if (path := Path(path)).is_file() else path \
        if path.is_dir() else None if none else path.parent


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


def which(data="sudo", raises: bool = False) -> str:
    """Checks if cmd or path is executable.

    Examples:
        >>> from nodeps import which
        >>> if which():
        ...    assert "sudo" in which()
        >>> assert which('/bin/ls') == '/bin/ls'
        >>> which("foo", raises=True) # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
        nodeps.CommandNotFoundError: foo

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
