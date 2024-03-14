import dataclasses
import os
import pathlib
import urllib
import urllib.parse
from collections.abc import Iterator, Mapping, Sequence
from typing import IO, Any, AnyStr, BinaryIO, Literal, TextIO, TypeAlias

from git import HEAD, Commit, IndexFile, Reference, Remote, Submodule, SymbolicReference, TagReference, Tree
from git.repo.base import BlameEntry
from git.types import TBD, CallableProgress, Commit_ish, Tree_ish

__all__: tuple[str, ...] = (
    "Repo",
)


try:
    # nodeps[repo] extras
    from git import Git as GitCmd  # type: ignore[attr-defined]
    from git import GitCmdObjectDB, GitConfigParser  # type: ignore[attr-defined]
    from git import Repo as GitRepo  # type: ignore[attr-defined]
    from git.refs.head import Head  # type: ignore[attr-defined]
    from git.util import IterableList  # type: ignore[attr-defined]
    from gitdb import LooseObjectDB  # type: ignore[attr-defined]
except ModuleNotFoundError:
    GitCmd: TypeAlias = None
    GitCmdObjectDB: TypeAlias = None
    GitConfigParser: TypeAlias = None
    GitRepo = object
    LooseObjectDB: TypeAlias = None

AnyPath: TypeAlias = os.PathLike | AnyStr | IO[AnyStr]
Lit_config_levels: TypeAlias = Literal["system", "global", "user", "repository"]
PathLike: TypeAlias = os.PathLike | str


@dataclasses.dataclass
class Repo(GitRepo):
    git: GitCmd = ...
    git_dir: AnyPath | None = ...
    odb: type[LooseObjectDB] = ...
    working_dir: AnyPath | None = ...
    path: dataclasses.InitVar[AnyPath | None] = ...
    expand_vars: dataclasses.InitVar[bool] = ...
    odbt: dataclasses.InitVar[type[LooseObjectDB]] = ...
    search_parent_directories: dataclasses.InitVar[bool] = ...

    def __init__(
            self,
            path: AnyPath | None = None,
            odbt: type[LooseObjectDB] = ...,
            search_parent_directories: bool = ...,
            expand_vars: bool = ...,
    ) -> None: ...

    def __post_init__(
            self,
            path: AnyPath | None,
            expand_vars: bool,
            odbt: type[LooseObjectDB],
            search_parent_directories: bool
    ) -> None: ...

    @property
    def active_branch(self) -> Head: ...

    def archive(
            self,
            ostream: TextIO | BinaryIO,
            treeish: str | None = None,
            prefix: str | None = None,
            **kwargs: Any,
    ) -> Repo: ...

    @property
    def bare(self) -> bool: ...

    def blame(
            self,
            rev: str | HEAD,
            file: str,
            incremental: bool = ...,
            rev_opts: list[str] | None = ...,
            **kwargs: Any,
    ) -> list[list[Commit | list[str | bytes] | None]] | Iterator[BlameEntry] | None: ...

    def blame_incremental(self, rev: str | HEAD, file: str, **kwargs: Any) -> Iterator[BlameEntry]: ...

    @property
    def branches(self) -> IterableList[Head]: ...

    def clone(
            self,
            path: PathLike,
            progress: CallableProgress | None = ...,
            multi_options: list[str] | None = ...,
            allow_unsafe_protocols: bool = ...,
            allow_unsafe_options: bool = ...,
            **kwargs: Any,
    ) -> Repo: ...

    @classmethod
    def clone_from(
            cls,
            url: PathLike,
            to_path: PathLike,
            progress: CallableProgress = ...,
            env: Mapping[str, str] | None = ...,
            multi_options: list[str] | None = ...,
            allow_unsafe_protocols: bool = ...,
            allow_unsafe_options: bool = ...,
            **kwargs: Any,
    ) -> Repo: ...

    def common_dir(self) -> PathLike: ...

    def config_reader(self, config_level: Lit_config_levels | None = ...) -> GitConfigParser: ...

    def config_writer(self, config_level: Lit_config_levels = ...) -> GitConfigParser: ...

    def create_head(
            self,
            path: PathLike,
            commit: SymbolicReference | str = ...,
            force: bool = False,
            logmsg: str | None = None,
    ) -> Head: ...

    def create_remote(self, name: str, url: str, **kwargs: Any) -> Remote: ...

    def create_submodule(self, *args: Any, **kwargs: Any) -> Submodule: ...

    def create_tag(
            self,
            path: PathLike,
            ref: str | SymbolicReference = ...,
            message: str | None = ...,
            force: bool = ...,
            **kwargs: Any,
    ) -> TagReference: ...

    def commit(self, rev: str | Commit_ish | None = ...) -> Commit: ...

    def currently_rebasing_on(self) -> Commit | None: ...

    def delete_remote(self, remote: Remote) -> str: ...

    def delete_head(self, *heads: str | Head, **kwargs: Any) -> None: ...

    def delete_tag(self, *tags: TagReference) -> None: ...

    @property
    def git_config(self) -> GitConfigParser: ...

    def has_separate_working_tree(self) -> bool: ...

    @property
    def head(self) -> HEAD: ...

    @property
    def heads(self) -> IterableList[Head]: ...

    def ignored(self, *paths: PathLike) -> list[str]: ...

    @property
    def index(self) -> IndexFile: ...

    @classmethod
    def init(
            cls,
            path: PathLike | None = ...,
            mkdir: bool = ...,
            odbt: type[GitCmdObjectDB] = ...,
            expand_vars: bool = ...,
            **kwargs: Any,
    ) -> Repo: ...

    def is_ancestor(self, ancestor_rev: Commit, rev: Commit) -> bool: ...

    def is_dirty(
            self,
            index: bool = ...,
            working_tree: bool = ...,
            untracked_files: bool = ...,
            submodules: bool = ...,
            path: PathLike | None = ...,
    ) -> bool: ...

    def is_valid_object(self, sha: str, object_type: str | None = ...) -> bool: ...

    def iter_commits(
            self,
            rev: str | Commit | SymbolicReference | None = ...,
            paths: PathLike | Sequence[PathLike] = ...,
            **kwargs: Any,
    ) -> Iterator[Commit]: ...

    def iter_submodules(self, *args: Any, **kwargs: Any) -> Iterator[Submodule]: ...

    def iter_trees(self, *args: Any, **kwargs: Any) -> Iterator[Tree]: ...

    def merge_base(self, *rev: TBD, **kwargs: Any) -> list[Commit_ish | None]: ...

    @property
    def references(self) -> IterableList[Reference]: ...

    def remote(self, name: str = ...) -> Remote: ...

    @property
    def remotes(self) -> IterableList[Remote]: ...

    @property
    def refs(self) -> IterableList[Reference]: ...

    @property
    def origin_url(self) -> urllib.parse.ParseResult: ...

    def submodule(self, name: str) -> Submodule: ...

    def submodule_update(self, *args: Any, **kwargs: Any) -> Iterator[Submodule]: ...

    @property
    def submodules(self) -> IterableList[Submodule]: ...

    def tag(self, path: PathLike) -> TagReference: ...

    @property
    def tags(self) -> IterableList[TagReference]: ...

    def tree(self, rev: Tree_ish | str | None = ...) -> Tree: ...

    @property
    def top(self) -> pathlib.Path: ...

    def untracked_files(self) -> list[str]: ...
