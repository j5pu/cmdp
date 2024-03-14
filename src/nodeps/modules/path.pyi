import configparser
import contextlib
import dataclasses
import os
import pathlib
import types
from collections.abc import Generator, Iterable, Iterator
from typing import IO, Any, AnyStr, Generic, Literal, TypeAlias, TypeVar, overload

from .typings import PathIsLiteral, StrOrBytesPath

__all__: tuple[str, ...] = (
    "FileConfig",
    "FrameSimple",
    "Passwd",
    "Path",
    "PathStat",

    "toiter",

    "AnyPath",
)
_T = TypeVar("_T")

ModeLiteral: TypeAlias = Literal[
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
]


@dataclasses.dataclass
class FileConfig:
    file: Path | None = ...
    config: dict | configparser.ConfigParser = ...


@dataclasses.dataclass
class FrameSimple:
    back: types.FrameType
    code: types.CodeType
    frame: types.FrameType
    function: str
    globals: dict[str, Any]  # noqa: A003
    lineno: int
    locals: dict[str, Any]  # noqa: A003
    name: str
    package: str
    path: Path
    vars: dict[str, Any]  # noqa: A003


@dataclasses.dataclass
class Passwd:
    data: dataclasses.InitVar[Passwd | AnyPath | str | int] = ...
    gid: int = ...
    gecos: str = ...
    group: str = ...
    groups: dict[str, int] = ...
    home: Path = ...
    shell: Path = ...
    uid: int = ...
    user: str = ...

    def __init__(self, data: Passwd | AnyPath | int | str = ...): ...

    def __post_init__(self, data: Passwd | AnyPath | int | str = ...): ...

    @property
    def is_su(self) -> bool: ...

    @property
    def is_sudo(self) -> bool: ...

    @property
    def is_user(self) -> bool: ...

    @classmethod
    def from_login(cls) -> Passwd: ...

    @classmethod
    def from_sudo(cls) -> Passwd: ...

    @classmethod
    def from_root(cls) -> Passwd: ...


class Path(pathlib.Path, pathlib.PurePosixPath, Generic[_T]):
    def __call__(
            self,
            name: AnyPath = ...,
            file: PathIsLiteral = ...,
            passwd: Passwd | AnyPath | str | int | None = ...,
            mode: int | str | None = ...,
            effective_ids: bool = ...,
            follow_symlinks: bool = ...,
    ) -> Path: ...

    def __contains__(self, value: Iterable) -> bool: ...

    def __eq__(self, other: Path) -> bool: ...

    def __hash__(self) -> int: ...

    def __iter__(self) -> Iterator[_T]: ...

    def __lt__(self, other: Path) -> bool: ...

    def __le__(self, other: Path) -> bool: ...

    def __gt__(self, other: Path) -> bool: ...

    def __ge__(self, other: Path) -> bool: ...

    def access(
            self,
            os_mode: int = ...,
            *,
            dir_fd: int | None = ...,
            effective_ids: bool = ...,
            follow_symlinks: bool = ...,
    ) -> bool | None: ...

    def add(self, *args: str, exception: bool = ...) -> Path: ...

    def append_text(self, text: str, encoding: str | None = ..., errors: str | None = ...) -> str: ...

    @overload
    @contextlib.contextmanager
    def cd(self) -> Generator[Path, None, None]: ...

    @overload
    def cd(self) -> Path: ...

    def chdir(self) -> Path: ...

    def checksum(
            self,
            algorithm: Literal["md5", "sha1", "sha224", "sha256", "sha384", "sha512"] = ...,
            block_size: int = ...,
    ) -> str: ...

    def chmod(
            self,
            mode: int | str | None = ...,
            effective_ids: bool = ...,
            exception: bool = ...,
            follow_symlinks: bool = ...,
            recursive: bool = ...,
    ) -> Path: ...

    def chown(
            self,
            passwd: Passwd | AnyPath | str | int = ...,
            effective_ids: bool = ...,
            exception: bool = ...,
            follow_symlinks: bool = ...,
            recursive: bool = ...,
    ) -> Path: ...

    def cmp(self, other: AnyPath) -> bool: ...

    def cp(
            self,
            dest: AnyPath,
            contents: bool = ...,
            effective_ids: bool = ...,
            follow_symlinks: bool = ...,
            preserve: bool = ...,
    ) -> Path: ...

    # noinspection PyMethodOverriding
    def exists(self) -> bool: ...

    @classmethod
    def expandvars(cls, path: str | None = ...) -> Path: ...

    def file_in_parents(self, exception: bool = ..., follow_symlinks: bool = ...) -> Path | None: ...

    def find_up(self, uppermost: bool = ...) -> Path | None: ...

    def has(self, value: Iterable) -> bool: ...

    def installed(self) -> bool: ...

    def ln(self, dest: AnyPath, force: bool = ...) -> Path: ...

    def ln_rel(self, dest: AnyPath) -> Path: ...

    def mkdir(
            self,
            name: AnyPath = ...,
            passwd: Passwd | AnyPath | str | int | None = ...,
            mode: int | str | None = ...,
            effective_ids: bool = ...,
            follow_symlinks: bool = ...,
    ) -> Path: ...

    def mv(self, dest: AnyPath) -> Path: ...

    def open(  # noqa: A003
            self,
            mode: str = ...,
            buffering: int = ...,
            encoding: str | None = ...,
            errors: str | None = ...,
            newline: str | None = ...,
            token: bool = ...,
    ) -> IO[AnyStr] | None: ...

    @classmethod
    def pickle(cls, data: _T | None = ..., name: Any = ..., rm: bool = ...) -> _T | None: ...

    def privileges(self, effective_ids: bool = ...): ...

    @classmethod
    def purelib(cls) -> Path: ...

    def realpath(self, exception: bool = ...) -> Path: ...

    def relative(self, path: AnyPath) -> Path | None: ...

    def rm(
            self, *args: str, effective_ids: bool = ..., follow_symlinks: bool = ..., missing_ok: bool = ...
    ) -> None: ...

    def rm_empty(self, preserve: bool = ...) -> None: ...

    def setid(
            self,
            name: bool | str | None = ...,
            uid: bool = ...,
            effective_ids: bool = ...,
            follow_symlinks: bool = ...,
    ) -> Path: ...

    @classmethod
    def setid_executable_is(cls) -> bool: ...

    @classmethod
    def setid_executable(cls) -> Path: ...

    @classmethod
    def setid_executable_cp(cls, name: str | None = ..., uid: bool = ...) -> Path: ...

    def stats(self, follow_symlinks: bool = ...) -> PathStat: ...

    def sudo(
            self,
            force: bool = ...,
            to_list: bool = ...,
            os_mode: int = ...,
            effective_ids: bool = ...,
            follow_symlinks: bool = ...,
    ) -> list[str] | str | None: ...

    def sys(self) -> None: ...

    @property
    def text(self) -> str: ...

    # noinspection PyNestedDecorators
    @overload
    @classmethod
    @contextlib.contextmanager
    def tempcd(
            cls, suffix: AnyStr | None = ..., prefix: AnyStr | None = ..., directory: AnyPath | None = ...
    ) -> Generator[Path, None, None]: ...

    # noinspection PyNestedDecorators
    @overload
    @classmethod
    def tempcd(
            cls, suffix: AnyStr | None = ..., prefix: AnyStr | None = ..., directory: AnyPath | None = ...
    ) -> Path: ...

    # noinspection PyNestedDecorators
    @overload
    @classmethod
    @contextlib.contextmanager
    def tempdir(
            cls, suffix: AnyStr | None = ..., prefix: AnyStr | None = ..., directory: AnyPath | AnyStr | None = ...
    ) -> Generator[Path, None, None]: ...

    # noinspection PyNestedDecorators
    @overload
    @classmethod
    def tempdir(
            cls, suffix: AnyStr | None = ..., prefix: AnyStr | None = ..., directory: AnyPath | AnyStr | None = ...
    ) -> Path: ...

    # noinspection PyNestedDecorators
    @overload
    @classmethod
    @contextlib.contextmanager
    def tempfile(
            cls,
            mode: ModeLiteral = ...,
            buffering: int = ...,
            encoding: str | None = ...,
            newline: str | None = ...,
            suffix: AnyStr | None = ...,
            prefix: AnyStr | None = ...,
            directory: AnyPath | None = ...,
            delete: bool = ...,
            *,
            errors: str | None = ...,
    ) -> Generator[Path, None, None]: ...

    # noinspection PyNestedDecorators
    @overload
    @classmethod
    def tempfile(
            cls,
            mode: ModeLiteral = ...,
            buffering: int = ...,
            encoding: str | None = ...,
            newline: str | None = ...,
            suffix: AnyStr | None = ...,
            prefix: AnyStr | None = ...,
            directory: AnyPath | None = ...,
            delete: bool = ...,
            *,
            errors: str | None = ...,
    ) -> Path: ...

    def to_parent(self) -> Path: ...

    def touch(
            self,
            name: AnyPath = ...,
            passwd: Passwd | Path | str | int | None = ...,
            mode: int | str | None = ...,
            effective_ids: bool = ...,
            follow_symlinks: bool = ...,
    ) -> Path: ...

    def with_suffix(self, suffix: str = ...) -> Path: ...


@dataclasses.dataclass
class PathStat:
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


def toiter(obj: Any, always: bool = ..., split: str = ...) -> Any: ...


AnyPath: TypeAlias = Path | StrOrBytesPath | IO[AnyStr]
