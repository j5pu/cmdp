"""Path Module."""
from __future__ import annotations

__all__ = (
    "FileConfig",
    "FrameSimple",
    "Passwd",
    "Path",
    "PathStat",

    "toiter",

    "AnyPath",
)

import contextlib
import dataclasses
import grp
import hashlib
import os
import pathlib
import pickle
import pwd
import stat
import subprocess
import sys
import sysconfig
import tempfile
import tokenize
from collections.abc import Iterable, Iterator
from typing import IO, TYPE_CHECKING, Any, AnyStr, Generic, Literal, TypeAlias, TypeVar, cast

from nodeps.modules.constants import MACOS, SUDO, USER
from nodeps.modules.errors import InvalidArgumentError
from nodeps.modules.typings import PathIsLiteral, StrOrBytesPath

if TYPE_CHECKING:
    import configparser
    import types

_T = TypeVar("_T")


@dataclasses.dataclass
class FileConfig:
    """FileConfig class."""

    file: Path | None = None
    config: dict | configparser.ConfigParser = dataclasses.field(default_factory=dict)


@dataclasses.dataclass
class FrameSimple:
    """Simple frame class."""

    back: types.FrameType
    code: types.CodeType
    frame: types.FrameType
    function: str
    globals: dict[str, Any]  # noqa: A003, A003
    lineno: int
    locals: dict[str, Any]  # noqa: A003
    name: str
    package: str
    path: Path
    vars: dict[str, Any]  # noqa: A003


@dataclasses.dataclass
class Passwd:
    """Passwd class from either `uid` or `user`.

    Args:
    -----
        uid: int
            User ID
        user: str
            Username

    Attributes:
    -----------
        gid: int
            Group ID
        gecos: str
            Full name
        group: str
            Group name
        groups: tuple(str)
            Groups list
        home: Path
            User's home
        shell: Path
            User shell
        uid: int
            User ID (default: :func:`os.getuid` current user id)
        user: str
            Username
    """
    data: dataclasses.InitVar[Passwd | AnyPath | str | int] = USER
    gid: int = dataclasses.field(default=None, init=False)
    gecos: str = dataclasses.field(default=None, init=False)
    group: str = dataclasses.field(default=None, init=False)
    groups: dict[str, int] = dataclasses.field(default=None, init=False)
    home: Path = dataclasses.field(default=None, init=False)
    shell: Path = dataclasses.field(default=None, init=False)
    uid: int = dataclasses.field(default=None, init=False)
    user: str = dataclasses.field(default=None, init=False)

    def __post_init__(self, data: Passwd | AnyPath | int | str = USER):
        """Instance of :class:`nodeps:Passwd`  from either `uid` or `user` (default: :func:`os.getuid`).

        Uses completed/real id's (os.getgid, os.getuid) instead effective id's (os.geteuid, os.getegid) as default.
            - UID and GID: when login from $LOGNAME, $USER or os.getuid()
            - RUID and RGID: completed real user id and group id inherit from UID and GID
                (when completed start EUID and EGID and set to the same values as RUID and RGID)
            - EUID and EGID: if executable has 'setuid' or 'setgid' (i.e: ping, sudo), EUID and EGID are changed
                to the owner (setuid) or group (setgid) of the binary.
            - SUID and SGID: if executable has 'setuid' or 'setgid' (i.e: ping, sudo), SUID and SGID are saved with
                RUID and RGID to do unprivileged tasks by a privileged completed (had 'setuid' or 'setgid').
                Can not be accessed in macOS with `os.getresuid()` and `os.getresgid()`

        Examples:
            >>> import pathlib
            >>> from nodeps import MACOS, USER, SUDO
            >>> from nodeps import Passwd
            >>> from nodeps import Path
            >>>
            >>> default = Passwd()
            >>> login = Passwd.from_login()
            >>>
            >>> assert default == Passwd(Path()) == Passwd(pathlib.Path())  == Passwd(USER) == Passwd(os.getuid()) == \
                    login
            >>> if SUDO:
            ...     assert default != Passwd().from_root()
            ... else:
            ...     assert default == Passwd().from_root()
            >>> assert default.gid == os.getgid()
            >>> if home := os.environ.get("HOME"):
            ...     assert default.home == Path(home)
            >>> if shell := os.environ.get("SHELL"):
            ...     assert default.shell == Path(shell)
            >>> assert default.uid == os.getuid()
            >>> assert default.user == USER
            >>> if MACOS:
            ...    assert "staff" in default.groups
            ...    assert "admin" in default.groups

        Errors:
            os.setuid(0)
            os.seteuid(0)
            os.setreuid(0, 0)

        os.getuid()
        os.geteuid(
        os.setuid(uid) can only be used if running as root in macOS.
        os.seteuid(euid) -> 0
        os.setreuid(ruid, euid) -> sets EUID and RUID (probar con 501, 0)
        os.setpgid(os.getpid(), 0) -> sets PGID and RGID (probar con 501, 0)

        Returns:
            Instance of :class:`nodeps:Passwd`
        """
        if isinstance(data, self.__class__):
            self.__dict__.update(data.__dict__)
            return

        if (isinstance(data, str) and not data.isnumeric()) or isinstance(data, pathlib.PurePosixPath):
            passwd = pwd.getpwnam(cast(str, getattr(data, "owner", lambda: None)() or data))
        else:
            passwd = pwd.getpwuid(int(data) if data or data == 0 else os.getuid())

        self.gid = passwd.pw_gid
        self.gecos = passwd.pw_gecos
        self.home = Path(passwd.pw_dir)
        self.shell = Path(passwd.pw_shell)
        self.uid = passwd.pw_uid
        self.user = passwd.pw_name

        group = grp.getgrgid(self.gid)
        self.group = group.gr_name
        self.groups = {grp.getgrgid(gid).gr_name: gid for gid in os.getgrouplist(self.user, self.gid)}

    @property
    def is_su(self) -> bool:
        """Returns True if login as root, uid=0 and not `SUDO_USER`."""
        return self.uid == 0 and not bool(os.environ.get("SUDO_USER"))

    @property
    def is_sudo(self) -> bool:
        """Returns True if SUDO_USER is set."""
        return bool(os.environ.get("SUDO_USER"))

    @property
    def is_user(self) -> bool:
        """Returns True if user and not `SUDO_USER`."""
        return self.uid != 0 and not bool(os.environ.get("SUDO_USER"))

    @classmethod
    def from_login(cls) -> Passwd:
        """Returns instance of :class:`nodeps:Passwd` from '/dev/console' on macOS and `os.getlogin()` on Linux."""
        try:
            user = Path("/dev/console").owner() if MACOS else os.getlogin()
        except OSError:
            user = Path("/proc/self/loginuid").owner()
        return cls(user)

    @classmethod
    def from_sudo(cls) -> Passwd:
        """Returns instance of :class:`nodeps:Passwd` from `SUDO_USER` if set or current user."""
        uid = os.environ.get("SUDO_UID", os.getuid())
        return cls(uid)

    @classmethod
    def from_root(cls) -> Passwd:
        """Returns instance of :class:`nodeps:Passwd` for root."""
        return cls(0)


class Path(pathlib.Path, pathlib.PurePosixPath, Generic[_T]):
    """Path helper class."""

    def __call__(
            self,
            name: AnyPath = "",
            file: PathIsLiteral = "is_dir",
            passwd: Passwd | AnyPath | str | int | None = None,
            mode: int | str | None = None,
            effective_ids: bool = True,
            follow_symlinks: bool = False,
    ) -> Path:
        """Make dir or touch file and create subdirectories as needed.

        Examples:
            >>> from nodeps import Path
            >>>
            >>> with Path.tempdir() as t:
            ...     p = t('1/2/3/4')
            ...     assert p.is_dir() is True
            ...     p = t('1/2/3/4/5/6/7.py', file="is_file")
            ...     assert p.is_file() is True
            ...     t('1/2/3/4/5/6/7.py/8/9.py', file="is_file") # doctest: +IGNORE_EXCEPTION_DETAIL, +ELLIPSIS
            Traceback (most recent call last):
            NotADirectoryError: File: ...

        Args:
            name: path to add.
            file: file or directory.
            passwd: user.
            mode: mode.
            effective_ids: If True, access will use the effective uid/gid instead of
            follow_symlinks: resolve self if self is symlink (default: True).

        Returns:
            Path.
        """
        # noinspection PyArgumentList
        return (self.mkdir if file in ["is_dir", "exists"] else self.touch)(
            name=name,
            passwd=passwd,
            mode=mode,
            effective_ids=effective_ids,
            follow_symlinks=follow_symlinks,
        )

    def __contains__(self, value: Iterable) -> bool:
        """Checks all items in value exist in self.resolve().

        To check only parts use self.has.

        Examples:
            >>> from nodeps import Path
            >>> from nodeps import USER
            >>>
            >>> assert '/usr' in Path('/usr/local')
            >>> assert 'usr local' in Path('/usr/local')
            >>> assert 'home' not in Path('/usr/local')
            >>> assert '' not in Path('/usr/local')
            >>> assert '/' in Path()
            >>> assert USER in Path.home()

        Args:
            value: space separated list of items to check, or iterable of items.

        Returns:
            bool
        """
        value = self.__class__(value) if isinstance(value, str) and "/" in value else toiter(value)
        return all(item in self.resolve().parts for item in value)

    def __eq__(self, other: Path) -> bool:
        """Equal based on parts.

        Examples:
            >>> from nodeps import Path
            >>>
            >>> assert Path('/usr/local') == Path('/usr/local')
        """
        if not isinstance(other, self.__class__):
            return NotImplemented
        return tuple(self.parts) == tuple(other.parts)

    def __hash__(self) -> int:
        """Hash based on parts."""
        return self._hash if hasattr(self, "_hash") else hash(tuple(self.parts))

    def __iter__(self) -> Iterator[_T]:
        """Iterate over path parts.

        Examples:
            >>> from nodeps import Path
            >>>
            >>> assert list(Path('/usr/local')) == ['/', 'usr', 'local',]

        Returns:
            Iterable of path parts.
        """
        return iter(self.parts)

    def __lt__(self, other: Path) -> bool:
        """Less than based on parts."""
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.parts < other.parts

    def __le__(self, other: Path) -> bool:
        """Less than or equal based on parts."""
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.parts <= other.parts

    def __gt__(self, other: Path) -> bool:
        """Greater than based on parts."""
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.parts > other.parts

    def __ge__(self, other: Path) -> bool:
        """Greater than or equal based on parts."""
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.parts >= other.parts

    def access(
            self,
            os_mode: int = os.W_OK,
            *,
            dir_fd: int | None = None,
            effective_ids: bool = True,
            follow_symlinks: bool = False,
    ) -> bool | None:
        # noinspection LongLine
        """Checks if file or directory exists and has access (returns None if file/directory does not exist.

        Use the real uid/gid to test for access to a path `Real Effective IDs.`_.

        -   real: user owns the completed.
        -   effective: user invoking.

        Examples:
            >>> import os
            >>> from nodeps import Path
            >>> from nodeps import MACOS
            >>> from nodeps import LOCAL
            >>> from nodeps import USER
            >>>
            >>> assert Path().access() is True
            >>> if USER == "root":
            ...     assert Path('/usr/bin').access() is True
            ... else:
            ...     assert Path('/usr/bin').access() is False
            >>> assert Path('/tmp').access(follow_symlinks=True) is True
            >>> assert Path('/tmp').access(effective_ids=False, follow_symlinks=True) is True
            >>> if MACOS and LOCAL:
            ...     assert Path('/etc/bashrc').access(effective_ids=False) is False
            ...     assert Path('/etc/sudoers').access(effective_ids=False, os_mode=os.R_OK) is False


        Args:
            os_mode: Operating-system mode bitfield. Can be F_OK to test existence,
                or the inclusive-OR of R_OK, W_OK, and X_OK (default: `os.W_OK`).
            dir_fd: If not None, it should be a file descriptor open to a directory,
                and path should be relative; path will then be relative to that
                directory.
            effective_ids: If True, access will use the effective uid/gid instead of
                the real uid/gid (default: True).
            follow_symlinks: If False, and the last element of the path is a symbolic link,
                access will examine the symbolic link itself instead of the file
                the link points to (default: False).

        Note:
            Most operations will use the effective uid/gid (what the operating system
            looks at to make a decision whether you are allowed to do something), therefore this
            routine can be used in a suid/sgid environment to test if the invoking user
            has the specified access to the path.

            When a setuid program (`-rwsr-xr-x`) executes, the completed changes its Effective User ID (EUID)
            from the default RUID to the owner of this special binary executable file:

                -   euid: owner of executable (`os.geteuid()`).
                -   uid: user starting the completed (`os.getuid()`).

        Returns:
            True if access.

        See Also:
        `Real Effective IDs.
        <https://stackoverflow.com/questions/32455684/difference-between-real-user-id-effective-user-id-and-saved
        -user-id>`_
        """
        if not self.exists():
            return None
        return os.access(
            self,
            mode=os_mode,
            dir_fd=dir_fd,
            effective_ids=effective_ids,
            follow_symlinks=follow_symlinks,
        )

    def add(self, *args: str, exception: bool = False) -> Path:
        """Add args to self.

        Examples:
            >>> from nodeps import Path
            >>> import nodeps
            >>>
            >>> p = Path().add('a/a')
            >>> assert Path() / 'a/a' == p
            >>> p = Path().add(*['a', 'a'])
            >>> assert Path() / 'a/a' == p
            >>> p = Path(nodeps.__file__)
            >>> p.add('a', exception=True)  # doctest: +IGNORE_EXCEPTION_DETAIL, +ELLIPSIS
            Traceback (most recent call last):
            FileNotFoundError...

        Args:
            *args: parts to be added.
            exception: raise exception if self is not dir and parts can not be added (default: False).

        Raises:
            FileNotFoundError: if self is not dir and parts can not be added.

        Returns:
            Compose path.
        """
        if exception and self.is_file() and args:
            msg = f"parts: {args}, can not be added since path is file or not directory: {self}"
            raise FileNotFoundError(msg)
        args = toiter(args)
        path = self
        for arg in args:
            path = path / arg
        return path

    def append_text(self, text: str, encoding: str | None = None, errors: str | None = None) -> str:
        """Open the file in text mode, append to it, and close the file (creates file if not file).

        Examples:
            >>> from nodeps import Path
            >>>
            >>> with Path.tempfile() as tmp:
            ...    _ = tmp.write_text('Hello')
            ...    assert 'Hello World!' in tmp.append_text(' World!')

        Args:
            text: text to add.
            encoding: encoding (default: None).
            errors: raise error if there is no file (default: None).

        Returns:
            File text with text appended.
        """
        if not isinstance(text, str):
            msg = f"data must be str, not {text.__class__.__name__}"
            raise TypeError(msg)
        with self.open(mode="a", encoding=encoding, errors=errors) as f:
            f.write(text)
        return self.read_text()

    @contextlib.contextmanager
    def cd(self) -> Path:
        """Change dir context manager to self if dir or parent if file and exists.

        Examples:
            >>> from nodeps import Path
            >>>
            >>> new = Path('/usr/local')
            >>> p = Path.cwd()
            >>> with new.cd() as prev:
            ...     assert new == Path.cwd()
            ...     assert prev == p
            >>> assert p == Path.cwd()

        Returns:
            Old Pwd Path.
        """
        oldpwd = self.cwd()
        try:
            self.chdir()
            yield oldpwd
        finally:
            oldpwd.chdir()

    def chdir(self) -> Path:
        """Change to self if dir or file parent if file and file exists.

        Examples:
            >>> from nodeps import Path
            >>>
            >>> new = Path(__file__).chdir()
            >>> assert new == Path(__file__).parent
            >>> assert Path.cwd() == new
            >>>
            >>> new = Path(__file__).parent
            >>> assert Path.cwd() == new
            >>>
            >>> Path("/tmp/foo").chdir()  # doctest: +IGNORE_EXCEPTION_DETAIL
            Traceback (most recent call last):
            FileNotFoundError: ... No such file or directory: '/tmp/foo'

        Raises:
            FileNotFoundError: No such file or directory if path does not exist.

        Returns:
            Path with changed directory.
        """
        path = self.to_parent()
        os.chdir(path)
        return path

    def checksum(
            self,
            algorithm: Literal["md5", "sha1", "sha224", "sha256", "sha384", "sha512"] = "sha256",
            block_size: int = 65536,
    ) -> str:
        """Calculate the checksum of a file.

        Examples:
            >>> from nodeps import Path
            >>>
            >>> with Path.tempfile() as tmp:
            ...    _ = tmp.write_text('Hello')
            ...    assert tmp.checksum() == '185f8db32271fe25f561a6fc938b2e264306ec304eda518007d1764826381969'

        Args:
            algorithm: hash algorithm (default: 'sha256').
            block_size: block size (default: 65536).

        Returns:
            Checksum of file.
        """
        sha = hashlib.new(algorithm)
        with self.open("rb") as f:
            for block in iter(lambda: f.read(block_size), b""):
                sha.update(block)
        return sha.hexdigest()

    def chmod(
            self,
            mode: int | str | None = None,
            effective_ids: bool = True,
            exception: bool = True,
            follow_symlinks: bool = False,
            recursive: bool = False,
    ) -> Path:
        """Change mode of self.

        Examples:
            >>> from nodeps import Path
            >>>
            >>> with Path.tempfile() as tmp:
            ...     changed = tmp.chmod(777)
            ...     assert changed.stat().st_mode & 0o777 == 0o777
            ...     assert changed.stats().mode == "-rwxrwxrwx"
            ...     assert changed.chmod("o-x").stats().mode == '-rwxrwxrw-'
            >>>
            >>> Path("/tmp/foo").chmod()  # doctest: +IGNORE_EXCEPTION_DETAIL
            Traceback (most recent call last):
            FileNotFoundError: ... No such file or directory: '/tmp/foo'

        Raises:
            FileNotFoundError: No such file or directory if path does not exist and exception is True.

        Args:
            mode: mode to change to (default: None).
            effective_ids: If True, access will use the effective uid/gid instead of
                the real uid/gid (default: False).
            follow_symlinks: resolve self if self is symlink (default: True).
            exception: raise exception if self does not exist (default: True).
            recursive: change owner of self and all subdirectories (default: False).

        Returns:
            Path with changed mode.
        """
        if exception and not self.exists():
            msg = f"path does not exist: {self}"
            raise FileNotFoundError(msg)

        subprocess.run(
            [
                *self.sudo(
                    force=True,
                    effective_ids=effective_ids,
                    follow_symlinks=follow_symlinks,
                ),
                f"{self.chmod.__name__}",
                *(["-R"] if recursive and self.is_dir() else []),
                str(mode or (755 if self.is_dir() else 644)),
                self.resolve() if follow_symlinks else self,
            ],
            capture_output=True,
        )

        return self

    def chown(
            self,
            passwd: Passwd | AnyPath | str | int = None,
            effective_ids: bool = True,
            exception: bool = True,
            follow_symlinks: bool = False,
            recursive: bool = False,
    ) -> Path:
        """Change owner of path.

        Examples:
            >>> from nodeps import Path
            >>> from nodeps import Passwd
            >>> from nodeps import MACOS
            >>>
            >>> with Path.tempfile() as tmp:
            ...     changed = tmp.chown(passwd=Passwd.from_root())
            ...     st = changed.stat()
            ...     assert st.st_gid == 0
            ...     assert st.st_uid == 0
            ...     stats = changed.stats()
            ...     assert stats.gid == 0
            ...     assert stats.uid == 0
            ...     assert stats.user == "root"
            ...     if MACOS:
            ...         assert stats.group == "wheel"
            ...         g = "admin"
            ...     else:
            ...         assert stats.group == "root"
            ...         g = "adm"
            ...     changed = tmp.chown(f"{os.getuid()}:{g}")
            ...     stats = changed.stats()
            ...     assert stats.group == g
            ...     assert stats.uid == os.getuid()
            >>>
            >>> Path("/tmp/foo").chown()  # doctest: +IGNORE_EXCEPTION_DETAIL
            Traceback (most recent call last):
            FileNotFoundError: ... No such file or directory: '/tmp/foo'

        Raises:
            FileNotFoundError: No such file or directory if path does not exist and exception is True.
            ValueError: passwd must be string with user:group.

        Args:
            passwd: user/group passwd to use, or string with user:group (default: None for USER).
            effective_ids: If True, access will use the effective uid/gid instead of
                the real uid/gid (default: False).
            exception: raise exception if self does not exist (default: True).
            follow_symlinks: resolve self if self is symlink (default: True).
            recursive: change owner of self and all subdirectories (default: False).

        Returns:
            Path with changed owner.
        """
        if exception and not self.exists():
            msg = f"path does not exist: {self}"
            raise FileNotFoundError(msg)

        if isinstance(passwd, str) and ":" in passwd:
            pass
        else:
            passwd = Passwd(passwd or USER)

        subprocess.run(
            [
                *self.sudo(
                    force=True,
                    effective_ids=effective_ids,
                    follow_symlinks=follow_symlinks,
                ),
                f"{self.chown.__name__}",
                *(["-R"] if recursive and self.is_dir() else []),
                f"{passwd.user}:{passwd.group}" if isinstance(passwd, Passwd) else passwd,
                self.resolve() if follow_symlinks else self,
            ],
            check=True,
            capture_output=True,
        )

        return self

    def cmp(self, other: AnyPath) -> bool:
        """Determine, whether two files provided to it are the same or not.

        By the same means that their contents are the same or not (excluding any metadata).
        Uses Cryptographic Hashes (using SHA256 - Secure hash algorithm 256) as a hash function.

        Examples:
            >>> from nodeps import Path
            >>> import nodeps
            >>> import asyncio
            >>>
            >>> assert Path(nodeps.__file__).cmp(nodeps.__file__) is True
            >>> assert Path(nodeps.__file__).cmp(asyncio.__file__) is False

        Args:
            other: other file to compare to

        Returns:
            True if equal.
        """
        return self.checksum() == self.__class__(other).checksum()

    def cp(
            self,
            dest: AnyPath,
            contents: bool = False,
            effective_ids: bool = True,
            follow_symlinks: bool = False,
            preserve: bool = False,
    ) -> Path:
        """Wrapper for shell `cp` command to copy file recursivily and adding sudo if necessary.

        Examples:
            >>> import sys
            >>> from nodeps import Path
            >>> from nodeps import SUDO, USER
            >>> from nodeps import Passwd
            >>>
            >>> with Path.tempfile() as tmp:
            ...     changed = tmp.chown(passwd=Passwd.from_root())
            ...     copied = Path(__file__).cp(changed)
            ...     st = copied.stat()
            ...     assert st.st_gid == 0
            ...     assert st.st_uid == 0
            ...     stats = copied.stats()
            ...     assert "-rw-" in stats.mode
            ...     _ = tmp.chown()
            ...     assert copied.cmp(__file__)

            >>> with Path.tempdir() as tmp:
            ...     _ = tmp.chmod("go+rx")
            ...     _ = tmp.chown(passwd=Passwd.from_root())
            ...     src = Path(__file__).parent
            ...     dirname = src.name
            ...     filename = Path(__file__).name
            ...
            ...     _ = src.cp(tmp)
            ...     destination = tmp / dirname
            ...     stats = destination.stats()
            ...     assert stats.mode == "drwxr-xr-x"
            ...     file = destination / filename
            ...     st = file.stat()
            ...     assert st.st_gid == 0
            ...     assert st.st_uid == 0
            ...     assert file.owner() == "root"
            ...     tmp = tmp.chown(recursive=True)
            ...     assert file.owner() == USER
            ...     assert file.cmp(__file__)
            ...
            ...     _ = src.cp(tmp, contents=True)
            ...     file = tmp / filename
            ...     assert file.cmp(__file__)
            >>>
            >>> Path("/tmp/foo").cp("/tmp/boo")  # doctest: +IGNORE_EXCEPTION_DETAIL
            Traceback (most recent call last):
            FileNotFoundError: ... No such file or directory: '/tmp/foo'

        Args:
            dest: destination.
            contents: copy contents of self to dest, `cp src/ dest` instead of `cp src dest` (default: False)`.
            effective_ids: If True, access will use the effective uid/gid instead of
                the real uid/gid (default: False).
            follow_symlinks: '-P' the 'cp' default, no symlinks are followed,
                all symbolic links are followed when True '-L' (actual files are copyed but if there are existing links
                will be left them untouched) (default: False)
                `-H` cp option is not implemented (default: False).
            preserve: preserve file attributes (default: False).

        Raises:
            FileNotFoundError: No such file or directory if path does not exist.

        Returns:
            Dest.
        """
        dest = self.__class__(dest)

        if not self.exists():
            msg = f"path does not exist: {self}"
            raise FileNotFoundError(msg)

        source = [self]
        if contents and self.is_dir() and len(files := list(self.iterdir())) > 0:
            # GNU: cp file/ /tmp -> does not copy the contents.
            source = files

        subprocess.run(
            [
                *dest.sudo(effective_ids=effective_ids, follow_symlinks=follow_symlinks),
                f"{self.cp.__name__}",
                *(["-R"] if self.is_dir() else []),
                *(["-L"] if follow_symlinks else []),
                *(["-p"] if preserve else []),
                *source,
                dest,
            ],
            check=True,
            capture_output=True,
        )

        return dest

    def exists(self) -> bool:
        """Check if file exists or is a broken link (super returns False if it is a broken link, we return True).

        Examples:
            >>> from nodeps import Path
            >>>
            >>> Path(__file__).exists()
            True
            >>> with Path.tempcd() as tmp:
            ...    source = tmp.touch("source")
            ...    destination = source.ln("destination")
            ...    assert destination.is_symlink()
            ...    source.unlink()
            ...    assert destination.exists()
            ...    assert not pathlib.Path(destination).exists()

        Returns:
            True if file exists or is broken link.
        """
        if super().exists():
            return True
        return self.is_symlink()

    @classmethod
    def expandvars(cls, path: str | None = None) -> Path:
        """Return a Path instance from expanded environment variables in path.

        Expand shell variables of form $var and ${var}.
        Unknown variables are left unchanged.

        Examples:
            >>> from nodeps import Path
            >>>
            >>> Path.expandvars('~/repo')  # doctest: +ELLIPSIS
            Path('~/repo')
            >>> Path.expandvars('${HOME}/repo')  # doctest: +ELLIPSIS
            Path('.../repo')

        Returns:
            Expanded Path.
        """
        return cls(os.path.expandvars(path) if path is not None else "")

    def file_in_parents(self, exception: bool = True, follow_symlinks: bool = False) -> Path | None:
        """Find up until file with name is found.

        Examples:
            >>> from nodeps import Path
            >>>
            >>> with Path.tempfile() as tmpfile:
            ...     new = tmpfile / "sub" / "file.py"
            ...     assert new.file_in_parents(exception=False) == tmpfile.absolute()
            >>>
            >>> with Path.tempdir() as tmpdir:
            ...    new = tmpdir / "sub" / "file.py"
            ...    assert new.file_in_parents() is None

        Args:
            exception: raise exception if a file is found in parents (default: False).
            follow_symlinks: resolve self if self is symlink (default: True).

        Raises:
            NotADirectoryError: ... No such file or directory: '/tmp/foo'

        Returns:
            File found in parents (str) or None
        """
        path = self.resolve() if follow_symlinks else self
        start = path
        while True:
            if path.is_file():
                if exception:
                    msg = f"File: {path} found in path: {start}"
                    raise NotADirectoryError(msg)
                return path
            if path.is_dir() or (
                    path := path.parent.resolve() if follow_symlinks else path.parent.absolute()
            ) == self.__class__("/"):
                return None

    def find_up(self, uppermost: bool = False) -> Path | None:
        """Find file or dir up.

        Examples:
            >>> import email.mime.application
            >>> import email
            >>> import email.mime
            >>> from nodeps import Path
            >>>
            >>> assert 'email/mime/__init__.py' in Path(email.mime.__file__, "__init__.py").find_up()
            >>> assert 'email/__init__.py' in Path(email.__file__, "__init__.py").find_up(uppermost=True)


        Args:
            uppermost: find uppermost (default: False).

        Returns:
            FindUp:
        """
        start = self.absolute().parent
        latest = None
        found = None
        while True:
            find = start / self.name
            if find.exists():
                found = find
                if not uppermost:
                    return find
                latest = find
            start = start.parent
            if start == Path("/"):
                return latest if latest is not None and latest.exists() else found

    def has(self, value: Iterable) -> bool:
        """Checks all items in value exist in `self.parts` (not absolute and not relative).

        Only checks parts and not resolved as checked by __contains__ or absolute.

        Examples:
            >>> from nodeps import Path
            >>>
            >>> assert Path('/usr/local').has('/usr') is True
            >>> assert Path('/usr/local').has('usr local') is True
            >>> assert Path('/usr/local').has('home') is False
            >>> assert Path('/usr/local').has('') is False

        Args:
            value: space separated list of items to check, or iterable of items.

        Returns:
            bool
        """
        value = self.__class__(value) if isinstance(value, str) and "/" in value else toiter(value)
        return all(item in self.parts for item in value)

    def installed(self) -> bool:
        """Check if file is installed.

        Examples:
            >>> import pytest
            >>> from nodeps import Path
            >>>
            >>> assert Path(pytest.__file__).installed() is True
        """
        return self.is_relative_to(self.purelib())

    def ln(self, dest: AnyPath, force: bool = True) -> Path:
        """Wrapper for super `symlink_to` to return the new path and changing the argument.

        If symbolic link already exists and have the same source, it will not be overwritten.

        Similar:

            - dest.symlink_to(src)
            - src.ln(dest) -> dest
            - os.symlink(src, dest)

        Examples:
            >>> from nodeps import Path
            >>>
            >>> with Path.tempcd() as tmp:
            ...     source = tmp.touch("source")
            ...     _ = source.ln("destination")
            ...     destination = source.ln("destination")
            ...     assert destination.is_symlink()
            ...     assert destination.resolve() == source.resolve()
            ...     assert destination.readlink().resolve() == source.resolve()
            ...
            ...     touch = tmp.touch("touch")
            ...     _ = tmp.ln("touch", force=False)  # doctest: +IGNORE_EXCEPTION_DETAIL
            Traceback (most recent call last):
            FileExistsError:

        Raises:
            FileExistsError: if dest already exists or is a symbolic link with different source and force is False.

        Args:
           dest: link destination (ln -s self dest)
           force: force creation of link, if file or link exists and is different (default: True)
        """
        dest = self.__class__(dest)
        if dest.is_symlink() and dest.readlink().resolve() == self.resolve():
            return dest
        if force and dest.exists():
            dest.rm()
        os.symlink(self, dest)
        return dest

    def ln_rel(self, dest: AnyPath) -> Path:
        """Create a symlink pointing to ``target`` from ``location``.

        Args:
            dest: The location of the symlink itself.
        """
        # HACER: examples and check if exists and merge with ln with absolute argument.
        target = self
        destination = self.__class__(dest)
        target_dir = destination.parent
        target_dir.mkdir()
        relative_source = os.path.relpath(target, target_dir)
        dir_fd = os.open(str(target_dir.absolute()), os.O_RDONLY)
        print(f"{relative_source} -> {destination.name} in {target_dir}")
        try:
            os.symlink(relative_source, destination.name, dir_fd=dir_fd)
        finally:
            os.close(dir_fd)

        return destination

    def mkdir(
            self,
            name: AnyPath = "",
            passwd: Passwd | AnyPath | str | int | None = None,
            mode: int | str | None = None,
            effective_ids: bool = True,
            follow_symlinks: bool = False,
    ) -> Path:
        """Add directory, make directory, change mode and return new Path.

        Examples:
            >>> import getpass
            >>> from nodeps import Path
            >>> from nodeps import Passwd
            >>>
            >>> with Path.tempcd() as tmp:
            ...     directory = tmp('1/2/3/4')
            ...     assert directory.is_dir() is True
            ...     assert directory.owner() == getpass.getuser()
            ...
            ...     _ = directory.chown(passwd=Passwd.from_root())
            ...     assert directory.owner() == "root"
            ...     five = directory.mkdir("5")
            ...     assert five.text.endswith('/1/2/3/4/5') is True
            ...     assert five.owner() == "root"
            ...
            ...     six = directory("6")
            ...     assert six.owner() == "root"
            ...
            ...     seven = directory("7", passwd=Passwd())
            ...     assert seven.owner() == getpass.getuser()
            ...
            ...     _ = directory.chown(passwd=Passwd())

        Args:
            name: name.
            passwd: group/user for chown, if None ownership will not be changed (default: None).
            mode: mode.
            effective_ids: If True, access will use the effective uid/gid instead of
                the real uid/gid (default: True).
            follow_symlinks: resolve self if self is symlink (default: True).

        Raises:
            NotADirectoryError: Directory can not be made because it's a file.

        Returns:
            Path:
        """
        path = (self / str(name)).resolve() if follow_symlinks else (self / str(name))
        if not path.is_dir() and path.file_in_parents(follow_symlinks=follow_symlinks) is None:
            subprocess.run(
                [
                    *path.sudo(effective_ids=effective_ids, follow_symlinks=follow_symlinks),
                    f"{self.mkdir.__name__}",
                    "-p",
                    *(["-m", str(mode)] if mode else []),
                    path,
                ],
                capture_output=True,
            )

            if passwd is not None:
                path.chown(
                    passwd=passwd,
                    effective_ids=effective_ids,
                    follow_symlinks=follow_symlinks,
                )
        return path

    def mv(self, dest: AnyPath) -> Path:
        """Move.

        Examples:
            >>> from nodeps import Path
            >>>
            >>> with Path.tempdir() as tmp:
            ...     name = 'dir'
            ...     pth = tmp(name)
            ...     assert pth.is_dir()
            ...     _ = pth.mv(tmp('dir2'))
            ...     assert not pth.is_dir()
            ...     assert tmp('dir2').is_dir()
            ...     name = 'file'
            ...     pth = tmp(name, "is_file")
            ...     assert pth.is_file()
            ...     _ = pth.mv(tmp('file2'))
            ...     assert not pth.is_file()

        Args:
            dest: destination.

        Returns:
            None.
        """
        subprocess.run(
            [*self.__class__(dest).sudo(), f"{self.mv.__name__}", self, dest],
            check=True,
            capture_output=True,
        )
        return dest

    def open(  # noqa: A003
            self,
            mode: str = "r",
            buffering: int = -1,
            encoding: str | None = None,
            errors: str | None = None,
            newline: str | None = None,
            token: bool = False,
    ) -> IO[AnyStr] | None:
        """Open the file pointed by this path and return a file object, as the built-in open function does."""
        if token:
            return tokenize.open(self.text) if self.is_file() else None
        return super().open(
            mode=mode,
            buffering=buffering,
            encoding=encoding,
            errors=errors,
            newline=newline,
        )

    @classmethod
    def pickle(cls, data: _T | None = None, name: Any = None, rm: bool = False) -> _T | None:
        """Load or dumps pickle file from ~/.pickle directory.

        Examples:
            >>> import pickle
            >>> from nodeps import Path
            >>>
            >>> assert Path.pickle(name="test") is None
            >>>
            >>> obj = {'a': 1}
            >>> _ = Path.pickle(obj, name="test")
            >>> assert Path.pickle(name="test") == obj
            >>>
            >>> obj2 = {'a': 2}
            >>> _ = Path.pickle(obj2, name="test", rm=True)
            >>> assert Path.pickle(name="test") == obj2
            >>>
            >>> assert Path.pickle(name="test", rm=True) is None

        Args:
            data: data to pickle (default: None to read from file).
            name: name.__name__ or name of object which will be used as file stem
                (default: None to get the name from __name__ in data)
            rm: rm existing data.

        Raises:
            InvalidArgumentError: when no name can be derived from data.__name__ or not name provided

        Returns:
            Pickle object (None if no data exists) if data is None else None.
        """
        name = getattr(name, "__name__", None) or name or getattr(data, "__name__", None)
        if name is None:
            msg = f"name must be provided if {data=} does not have attribute __name__"
            raise InvalidArgumentError(msg)
        name = name.replace("/", "_")

        if not (directory := cls("~/.pickle").expanduser()).exists():
            directory.mkdir()
        file = directory / f"{name}.pickle"

        if rm or (file.is_file() and file.stat().st_size == 0):
            file.rm()

        if data is None and file.is_file():
            with file.open("rb") as f:
                try:
                    return pickle.load(f)  # noqa: S301
                except ModuleNotFoundError:
                    file.rm()  # No module name if source has changed.
                    return None
        if data is None and not file.is_file():
            return None
        if data:
            with file.open("wb") as f:
                pickle.dump(data, f)
                return data
        return None

    def privileges(self, effective_ids: bool = True):
        """Return privileges of file.

        Args:
            effective_ids: If True, access will use the effective uid/gid instead of
                the real uid/gid (default: True).

        Returns:
            Privileges:
        """

    @classmethod
    def purelib(cls) -> Path:
        """Returns sysconfig purelib path."""
        return cls(sysconfig.get_paths()["purelib"])

    def realpath(self, exception: bool = False) -> Path:
        """Return the canonical path of the specified filename, eliminating any symbolic links encountered in the path.

        Examples:
            >>> from nodeps import Path
            >>>
            >>> assert Path('/usr/local').realpath() == Path('/usr/local')

        Args:
            exception: raise exception if path does not exist (default: False).

        Returns:
            Path with real path.
        """
        return self.__class__(os.path.realpath(self, strict=not exception))

    def relative(self, path: AnyPath) -> Path | None:
        """Return relative to path if is relative to path else None.

        Examples:
            >>> from nodeps import Path
            >>>
            >>> assert Path('/usr/local').relative('/usr') == Path('local')
            >>> assert Path('/usr/local').relative('/usr/local') == Path('.')
            >>> assert Path('/usr/local').relative('/usr/local/bin') is None

        Args:
            path: path.

        Returns:
            Relative path or None.
        """
        p = Path(path).absolute()
        return self.relative_to(p) if self.absolute().is_relative_to(p) else None

    def rm(
            self, *args: str, effective_ids: bool = True, follow_symlinks: bool = False, missing_ok: bool = True
    ) -> None:
        """Delete a folder/file (even if the folder is not empty).

        Examples:
            >>> from nodeps import Path
            >>>
            >>> with Path.tempdir() as tmp:
            ...     name = 'dir'
            ...     pth = tmp(name)
            ...     assert pth.is_dir()
            ...     pth.rm()
            ...     assert not pth.is_dir()
            ...     name = 'file'
            ...     pth = tmp(name, "is_file")
            ...     assert pth.is_file()
            ...     pth.rm()
            ...     assert not pth.is_file()
            ...     assert Path('/tmp/a/a/a/a')().is_dir()

        Raises:
            FileNotFoundError: ... No such file or directory: '/tmp/foo'

        Args:
            *args: parts to add to self.
            effective_ids: If True, access will use the effective uid/gid instead of
                the real uid/gid (default: False).
            follow_symlinks: True for resolved (default: False).
            missing_ok: missing_ok
        """
        if not missing_ok and not self.exists():
            msg = f"{self} does not exist"
            raise FileNotFoundError(msg)

        if (path := self.add(*args)).exists():
            subprocess.run(
                [
                    *path.sudo(
                        force=True,
                        effective_ids=effective_ids,
                        follow_symlinks=follow_symlinks,
                    ),
                    f"{self.rm.__name__}",
                    *(["-rf"] if self.is_dir() else []),
                    path.resolve() if follow_symlinks else path,
                ],
                capture_output=True,
            )

    def rm_empty(self, preserve: bool = True) -> None:
        """Remove empty directories recursive.

        Examples:
            >>> from nodeps import Path
            >>>
            >>> with Path.tempdir() as tmp:
            ...     first = tmp("1")
            ...
            ...     _ = tmp('1/2/3/4')
            ...     first.rm_empty()
            ...     assert first.exists() is True
            ...     assert Path("1").exists() is False
            ...
            ...     _ = tmp('1/2/3/4')
            ...     first.rm_empty(preserve=False)
            ...     assert first.exists() is False
            ...
            ...     _ = tmp('1/2/3/4/5/6/7.py', file="is_file")
            ...     first.rm_empty()
            ...     assert first.exists() is True

        Args:
            preserve: preserve top directory (default: True).

        """
        for directory, _, _ in os.walk(self, topdown=False):
            d = self.__class__(directory).absolute()
            if len(list(d.iterdir())) == 0 and (not preserve or (d != self.absolute() and preserve)):
                self.__class__(d).rmdir()

    def setid(
            self,
            name: bool | str | None = None,
            uid: bool = True,
            effective_ids: bool = True,
            follow_symlinks: bool = False,
    ) -> Path:
        """Sets the set-user-ID-on-execution or set-group-ID-on-execution bits.

        Works if interpreter binary is setuid `u+s,+x` (-rwsr-xr-x), and:

           - executable script and setuid interpreter on shebang (#!/usr/bin/env setuid_interpreter).
           - setuid_interpreter -m module (venv would be created as root

        Works if interpreter binary is setuid `g+s,+x` (-rwxr-sr-x), and:

        Examples:
            >>> from nodeps import Path
            >>>
            >>> with Path.tempdir() as p:
            ...     a = p.touch('a')
            ...     _ = a.setid()
            ...     assert a.stats().suid is True
            ...     _ = a.setid(uid=False)
            ...     assert a.stats().sgid is True
            ...
            ...     a.rm()
            ...
            ...     _ = a.touch()
            ...     b = a.setid('b')
            ...     assert b.stats().suid is True
            ...     assert a.cmp(b) is True
            ...
            ...     _ = b.setid('b', uid=False)
            ...     assert b.stats().sgid is True
            ...
            ...     _ = a.write_text('a')
            ...     assert a.cmp(b) is False
            ...     b = a.setid('b')
            ...     assert b.stats().suid is True
            ...     assert a.cmp(b) is True

        Args:
            name: name to rename if provided.
            uid: True to set UID bit, False to set GID bit (default: True).
            effective_ids: If True, access will use the effective uid/gid instead of
                the real uid/gid (default: False).
            follow_symlinks: True for resolved, False for absolute and None for relative
                or doesn't exist (default: True).

        Returns:
            Updated Path.
        """
        change = False
        chmod = f'{"u" if uid else "g"}+s,+x'
        mod = (stat.S_ISUID if uid else stat.S_ISGID) | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
        target = self.with_name(name) if name else self
        if name and (not target.exists() or not self.cmp(target)):
            self.cp(target, effective_ids=effective_ids, follow_symlinks=follow_symlinks)
            change = True
        elif target.stats().result.st_mode & mod != mod:
            change = True
        if target.owner() != "root":
            change = True
        if change:
            # First: chown, second: chmod
            target.chown(passwd=Passwd.from_root(), follow_symlinks=follow_symlinks)
            target.chmod(
                mode=chmod,
                effective_ids=effective_ids,
                follow_symlinks=follow_symlinks,
                recursive=True,
            )
        return target

    @classmethod
    def setid_executable_is(cls) -> bool:
        """True if Set user ID execution bit is set."""
        return cls(sys.executable).resolve().stat().st_mode & stat.S_ISUID == stat.S_ISUID

    @classmethod
    def setid_executable(cls) -> Path:
        """Sets the set-user-ID-on-execution bits for sys.executable.

        Returns:
            Updated Path.
        """
        return cls(sys.executable).resolve().setid()

    @classmethod
    def setid_executable_cp(cls, name: str | None = None, uid: bool = True) -> Path:
        r"""Sets the set-user-ID-on-execution or set-group-ID-on-execution bits for sys.executable.

        Examples:
            >>> import shutil
            >>> import subprocess
            >>> from nodeps import Path, MACOS, USER
            >>> def test():
            ...     f = Path.setid_executable_cp('setid_python_test')
            ...     assert subprocess.check_output([f, '-c', 'import os;print(os.geteuid())'], text=True) == '0\n'
            ...     if USER != "root":
            ...         assert subprocess.check_output([f, '-c', 'import os;print(os.getuid())'], text=True) != '0\n'
            ...     else:
            ...         assert subprocess.check_output([f, '-c', 'import os;print(os.getuid())'], text=True) == '0\n'
            ...     f.rm()
            ...     assert f.exists() is False
            >>> test()

        Args:
            name: name to rename if provided or False to add 'r' to original name (default: False).
            uid: True to set UID bit, False to set GID bit (default: True).

        Returns:
            Updated Path.
        """
        path = cls(sys.executable)
        return path.setid(name=name if name else f"r{path.name}", uid=uid)

    def stats(self, follow_symlinks: bool = False) -> PathStat:
        """Return result of the stat() system call on this path, like os.stat() with extra parsing for bits and root.

        Examples:
            >>> from nodeps import Path
            >>>
            >>> rv = Path().stats()
            >>> assert all([rv.root, rv.sgid, rv.sticky, rv.suid]) is False
            >>>
            >>> with Path.tempfile() as file:
            ...     _ = file.chmod('u+s,+x')
            ...     assert file.stats().suid is True
            ...     _ = file.chmod('g+s,+x')
            ...     assert file.stats().sgid is True

        Args:
            follow_symlinks: If False, and the last element of the path is a symbolic link,
                stat will examine the symbolic link itself instead of the file
                the link points to (default: False).

        Returns:
            PathStat namedtuple :class:`nodeps.PathStat`:
            gid: file GID
            group: file group name
            mode: file mode string formatted as '-rwxrwxrwx'
            own: user and group string formatted as 'user:group'
            passwd: instance of :class:`nodeps:Passwd` for file owner
            result: result of `os.stat`
            root: is owned by root
            sgid: group executable and sticky bit (GID bit), members execute as the executable group (i.e.: crontab)
            sticky: sticky bit (directories), new files created in this directory will be owned by the directory's owner
            suid: user executable and sticky bit (UID bit), user execute and as the executable owner (i.e.: sudo)
            uid: file UID
            user: file owner name
        """
        mapping = {
            "sgid": stat.S_ISGID | stat.S_IXGRP,
            "suid": stat.S_ISUID | stat.S_IXUSR,
            "sticky": stat.S_ISVTX,
        }
        result = super().stat(follow_symlinks=follow_symlinks)
        passwd = Passwd(result.st_uid)
        # noinspection PyArgumentList
        return PathStat(
            gid=result.st_gid,
            group=grp.getgrgid(result.st_gid).gr_name,
            mode=stat.filemode(result.st_mode),
            own=f"{passwd.user}:{passwd.group}",
            passwd=passwd,
            result=result,
            root=result.st_uid == 0,
            uid=result.st_uid,
            user=passwd.user,
            **{i: result.st_mode & mapping[i] == mapping[i] for i in mapping},
        )

    def sudo(
            self,
            force: bool = False,
            to_list: bool = True,
            os_mode: int = os.W_OK,
            effective_ids: bool = True,
            follow_symlinks: bool = False,
    ) -> list[str] | str | None:
        """Returns sudo command if path or ancestors exist and is not own by user and sudo command not installed.

        Examples:
            >>> from nodeps import which
            >>> from nodeps import Path
            >>> from nodeps import SUDO
            >>>
            >>> assert Path('/tmp').sudo(to_list=False, follow_symlinks=True) == ''
            >>> if SUDO:
            ...     assert "sudo" in Path('/usr/bin').sudo(to_list=False)
            >>> assert Path('/usr/bin/no_dir/no_file.text').sudo(to_list=False) == SUDO
            >>> assert Path('no_dir/no_file.text').sudo(to_list=False) == ''
            >>> assert Path('/tmp').sudo(follow_symlinks=True) == []
            >>> if SUDO:
            ...     assert Path('/usr/bin').sudo() == [SUDO]
            ... else:
            ...     assert Path('/usr/bin').sudo() == []

        Args:
            force: if sudo installed and user is not root, return always sudo path
            to_list: return starred/list for command with no shell (default: True).
            os_mode: Operating-system mode bitfield. Can be F_OK to test existence,
                or the inclusive-OR of R_OK, W_OK, and X_OK (default: `os.W_OK`).
            effective_ids: If True, access will use the effective uid/gid instead of
                the real uid/gid (default: True).
            follow_symlinks: If False, and the last element of the path is a symbolic link,
                access will examine the symbolic link itself instead of the file
                the link points to (default: False).

        Returns:
            `sudo` or "", str or list.
        """
        rv = SUDO
        if rv and (os.geteuid if effective_ids else os.getuid)() != 0:
            path = self
            while path:
                if path.access(
                    os_mode=os_mode,
                    effective_ids=effective_ids,
                    follow_symlinks=follow_symlinks,
                ):
                    if not force:
                        rv = ""
                    break
                if path.exists() or str(path := (path.parent.resolve() if follow_symlinks else path.parent)) == "/":
                    break
        return ([rv] if rv else []) if to_list else rv

    def sys(self) -> None:
        """Insert self absolute if exists to sys.path 0 if it is not in sys.path.

        Examples:
            >>> import sys
            >>> from nodeps import Path
            >>>
            >>> cwd = Path.cwd()
            >>> cwd.sys()
            >>> assert str(cwd.absolute()) in sys.path
        """
        absolute = self.absolute()
        if absolute.exists() and absolute.__str__() not in sys.path:
            sys.path.insert(0, absolute.__str__())

    @property
    def text(self) -> str:
        """Path as text.

        Examples:
            >>> from nodeps import Path
            >>>
            >>> assert Path('/usr/local').text == '/usr/local'

        Returns:
            Path string.
        """
        return str(self)

    @classmethod
    @contextlib.contextmanager
    def tempcd(
            cls, suffix: AnyStr | None = None, prefix: AnyStr | None = None, directory: AnyPath | None = None
    ) -> Path:
        """Create temporaly directory, change to it and return it.

        This has the same behavior as mkdtemp but can be used as a context manager.

        Upon exiting the context, the directory and everything contained
        in it are removed.

        Examples:
            >>> from nodeps import Path
            >>>
            >>> work = Path.cwd()
            >>> with Path.tempcd() as tmp:
            ...     assert tmp.exists() and tmp.is_dir()
            ...     assert Path.cwd() == tmp.resolve()
            >>> assert work == Path.cwd()
            >>> assert tmp.exists() is False

        Args:
            suffix: If 'suffix' is not None, the directory name will end with that suffix,
                otherwise there will be no suffix. For example, .../T/tmpy5tf_0suffix
            prefix: If 'prefix' is not None, the directory name will begin with that prefix,
                otherwise a default prefix is used.. For example, .../T/prefixtmpy5tf_0
            directory: If 'directory' is not None, the directory will be created in that directory (must exist,
                otherwise a default directory is used. For example, DIRECTORY/tmpy5tf_0

        Returns:
            Directory Path.
        """
        with cls.tempdir(suffix=suffix, prefix=prefix, directory=directory) as tmpdir, tmpdir.cd():
            try:
                yield tmpdir
            finally:
                pass

    @classmethod
    @contextlib.contextmanager
    def tempdir(
            cls, suffix: AnyStr | None = None, prefix: AnyStr | None = None, directory: AnyPath | None = None
    ) -> Path:
        """Create and return tmp directory.  This has the same behavior as mkdtemp but can be used as a context manager.

        Upon exiting the context, the directory and everything contained in it are removed.

        Examples:
            >>> from nodeps import Path
            >>>
            >>> work = Path.cwd()
            >>> with Path.tempdir() as tmpdir:
            ...     assert tmpdir.exists() and tmpdir.is_dir()
            ...     assert Path.cwd() != tmpdir
            ...     assert work == Path.cwd()
            >>> assert tmpdir.exists() is False

        Args:
            suffix: If 'suffix' is not None, the directory name will end with that suffix,
                otherwise there will be no suffix. For example, .../T/tmpy5tf_0suffix
            prefix: If 'prefix' is not None, the directory name will begin with that prefix,
                otherwise a default prefix is used.. For example, .../T/prefixtmpy5tf_0
            directory: If 'directory' is not None, the directory will be created in that directory (must exist,
                otherwise a default directory is used. For example, DIRECTORY/tmpy5tf_0

        Returns:
            Directory Path.
        """
        with tempfile.TemporaryDirectory(suffix=suffix, prefix=prefix, dir=directory) as tmp:
            try:
                yield cls(tmp)
            finally:
                pass

    @classmethod
    @contextlib.contextmanager
    def tempfile(
            cls,
            mode: Literal[
                "r",
                "w",
                "a",
                "x",
                "r+",
                "w+",
                "a+",
                "x+",
                "rt",
                "wt",
                "at",
                "xt",
                "r+t",
                "w+t",
                "a+t",
                "x+t",
            ] = "w",
            buffering: int = -1,
            encoding: str | None = None,
            newline: str | None = None,
            suffix: AnyStr | None = None,
            prefix: AnyStr | None = None,
            directory: AnyPath | None = None,
            delete: bool = True,
            *,
            errors: str | None = None,
    ) -> Path:
        """Create and return a temporary file.

        Examples:
            >>> from nodeps import Path
            >>>
            >>> with Path.tempfile() as tmpfile:
            ...    assert tmpfile.exists() and tmpfile.is_file()
            >>> assert tmpfile.exists() is False

        Args:
            mode: the mode argument to io.open (default "w+b").
            buffering:  the buffer size argument to io.open (default -1).
            encoding: the encoding argument to `io.open` (default None)
            newline: the newline argument to `io.open` (default None)
            delete: whether the file is deleted on close (default True).
            suffix: prefix for filename.
            prefix: prefix for filename.
            directory: directory.
            errors: the errors' argument to `io.open` (default None)

        Returns:
            An object with a file-like interface; the name of the file
            is accessible as its 'name' attribute.  The file will be automatically
            deleted when it is closed unless the 'delete' argument is set to False.
        """
        with tempfile.NamedTemporaryFile(
            mode=mode,
            buffering=buffering,
            encoding=encoding,
            newline=newline,
            suffix=suffix,
            prefix=prefix,
            dir=directory,
            delete=delete,
            errors=errors,
        ) as tmp:
            try:
                yield cls(tmp.name)
            finally:
                pass

    def to_parent(self) -> Path:
        """Return Parent if is file and exists or self.

        Examples:
            >>> from nodeps import Path
            >>>
            >>> assert Path(__file__).to_parent() == Path(__file__).parent

        Returns:
            Path of directory if is file or self.
        """
        return self.parent if self.is_file() else self

    def touch(
            self,
            name: AnyPath = "",
            passwd: Passwd | Path | str | int | None = None,
            mode: int | str | None = None,
            effective_ids: bool = True,
            follow_symlinks: bool = False,
    ) -> Path:
        """Add file, touch and return post_init Path. Parent paths are created.

        Examples:
            >>> from nodeps import Path
            >>> from nodeps import Passwd
            >>>
            >>> import getpass
            >>> with Path.tempcd() as tmp:
            ...     file = tmp('1/2/3/4/5/6/root.py', file="is_file", passwd=Passwd.from_root())
            ...     assert file.is_file() is True
            ...     assert file.parent.owner() == getpass.getuser()
            ...     assert file.owner() == "root"
            ...
            ...     new = file.parent("user.py", file="is_file")
            ...     assert new.owner() == getpass.getuser()
            ...
            ...     touch = file.parent.touch("touch.py")
            ...     assert touch.owner() == getpass.getuser()
            ...
            ...     last = (file.parent / "last.py").touch()
            ...     assert last.owner() == getpass.getuser()
            ...     assert last.is_file() is True
            ...
            ...     file.rm()

        Args:
            name: name.
            passwd: group/user for chown, if None ownership will not be changed (default: None).
            mode: mode.
            effective_ids: If True, access will use the effective uid/gid instead of
                the real uid/gid (default: False).
            follow_symlinks: If False, I think is useless (default: False).

        Returns:
            Path.
        """
        path = self / str(name)
        path = path.resolve() if follow_symlinks else path.absolute()
        if (
                not path.is_file()
                and not path.is_dir()
                and path.parent.file_in_parents(follow_symlinks=follow_symlinks) is None
        ):
            if not (d := path.parent).exists():
                d.mkdir(
                    mode=mode,
                    effective_ids=effective_ids,
                    follow_symlinks=follow_symlinks,
                )
            subprocess.run(
                [
                    *path.sudo(effective_ids=effective_ids, follow_symlinks=follow_symlinks),
                    f"{self.touch.__name__}",
                    path,
                ],
                capture_output=True,
                check=True,
            )
            path.chmod(mode=mode, effective_ids=effective_ids, follow_symlinks=follow_symlinks)
            if passwd is not None:
                path.chown(
                    passwd=passwd,
                    effective_ids=effective_ids,
                    follow_symlinks=follow_symlinks,
                )
        return path

    def with_suffix(self, suffix: str = "") -> Path:
        """Sets default for suffix to "", since :class:`pathlib.Path` does not have default.

        Return a new path with the file suffix changed.  If the path
        has no suffix, add given suffix.  If the given suffix is an empty
        string, remove the suffix from the path.

        Examples:
            >>> from nodeps import Path
            >>>
            >>> Path("/tmp/test.txt").with_suffix()
            Path('/tmp/test')

        Args:
            suffix: suffix (default: '')

        Returns:
            Path.
        """
        return super().with_suffix(suffix=suffix)


@dataclasses.dataclass
class PathStat:
    """Helper class for :func:`nodeps.Path.stats`.

    Args:
        gid: file GID
        group: file group name
        mode: file mode string formatted as '-rwxrwxrwx'
        own: user and group string formatted as 'user:group'
        passwd: instance of :class:`nodeps:Passwd` for file owner
        result: result of os.stat
        root: is owned by root
        sgid: group executable and sticky bit (GID bit), members execute as the executable group (i.e.: crontab)
        sticky: sticky bit (directories), new files created in this directory will be owned by the directory's owner
        suid: user executable and sticky bit (UID bit), user execute and as the executable owner (i.e.: sudo)
        uid: file UID
        user: file user name
    """

    gid: int
    group: str
    mode: str
    own: str
    passwd: Passwd
    result: os.stat_result
    root: bool
    sgid: bool
    sticky: bool
    suid: bool
    uid: int
    user: str


def toiter(obj: Any, always: bool = False, split: str = " ") -> Any:
    """To iter.

    Examples:
        >>> import pathlib
        >>> from nodeps import toiter
        >>>
        >>> assert toiter('test1') == ['test1']
        >>> assert toiter('test1 test2') == ['test1', 'test2']
        >>> assert toiter({'a': 1}) == {'a': 1}
        >>> assert toiter({'a': 1}, always=True) == [{'a': 1}]
        >>> assert toiter('test1.test2') == ['test1.test2']
        >>> assert toiter('test1.test2', split='.') == ['test1', 'test2']
        >>> assert toiter(pathlib.Path("/tmp/foo")) == ('/', 'tmp', 'foo')

    Args:
        obj: obj.
        always: return any iterable into a list.
        split: split for str.

    Returns:
        Iterable.
    """
    if isinstance(obj, str):
        obj = obj.split(split)
    elif hasattr(obj, "parts"):
        obj = obj.parts
    elif not isinstance(obj, Iterable) or always:
        obj = [obj]
    return obj


AnyPath: TypeAlias = Path | StrOrBytesPath | IO[AnyStr]
