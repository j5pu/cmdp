"""NoDeps Helpers and Utils Module."""
from __future__ import annotations

__all__ = (
    "CONSOLE",

    "Bump",
    "CalledProcessError",
    "Chain",
    "CmdError",
    "ColorLogger",
    "CommandNotFoundError",
    "dd",
    "dictsort",
    "Env",
    "EnvBuilder",
    "FileConfig",
    "FrameSimple",
    "getter",
    "Gh",
    "GitStatus",
    "GitUrl",
    "GroupUser",
    "InvalidArgumentError",
    "LetterCounter",
    "MyPrompt",
    "NamedtupleMeta",
    "Noset",
    "Passwd",
    "PathStat",
    "Path",
    "PipMetaPathFinder",
    "ProjectRepos",
    "Project",
    "PTHBuildPy",
    "PTHDevelop",
    "PTHEasyInstall",
    "PTHInstallLib",
    "TempDir",
    "aioclone",
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
    "clone",
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
    "ins",
    "is_idlelib",
    "is_repl",
    "is_terminal",
    "iscoro",
    "map_with_args",
    "mip",
    "noexc",
    "parent",
    "parse_str",
    "pipmetapathfinder",
    "returncode",
    "siteimported",
    "sourcepath",
    "split_pairs",
    "stdout",
    "stdquiet",
    "suppress",
    "syssudo",
    "tardir",
    "tilde",
    "timestamp_now",
    "to_camel",
    "toiter",
    "tomodules",
    "urljson",
    "varname",
    "which",
    "yield_if",
    "yield_last",
    "getstdout",
    "strip",
    "black",
    "red",
    "green",
    "yellow",
    "blue",
    "magenta",
    "cyan",
    "white",
    "bblack",
    "bred",
    "bgreen",
    "byellow",
    "bblue",
    "bmagenta",
    "bcyan",
    "bwhite",
    "reset",
    "COLORIZE",
    "EnumLower",
    "Color",
    "SYMBOL",
    "Symbol",
    "LOGGER_DEFAULT_FMT",
    "logger",
    "cache",
    "ic",
    "icc",
    "Repo",
    "PYTHON_FTP",
    "python_latest",
    "python_version",
    "python_versions",
    "request_x_api_key_json",
    "EXECUTABLE",
    "EXECUTABLE_SITE",
    "NOSET",
)

import abc
import ast
import asyncio
import collections
import contextlib
import copy
import dataclasses
import datetime
import enum
import filecmp
import fnmatch
import getpass
import grp
import hashlib
import importlib.abc
import importlib.metadata
import importlib.util
import inspect
import io
import ipaddress
import itertools
import json
import logging
import os
import pathlib
import pickle
import platform
import pwd
import re
import shutil
import signal
import stat
import string
import subprocess
import sys
import sysconfig
import tarfile
import tempfile
import textwrap
import threading
import time
import tokenize
import types
import urllib.error
import urllib.request
import venv
import warnings
import zipfile
from collections.abc import Callable, Generator, Hashable, Iterable, Iterator, Mapping, MutableMapping, Sequence
from io import BufferedRandom, BufferedReader, BufferedWriter, FileIO, TextIOWrapper
from ipaddress import IPv4Address, IPv6Address
from typing import (
    IO,
    TYPE_CHECKING,
    Any,
    AnyStr,
    BinaryIO,
    ClassVar,
    Generic,
    Literal,
    ParamSpec,
    TextIO,
    TypeAlias,
    TypeVar,
    Union,
    cast,
)


# <editor-fold desc="nodeps[pth] extras">
try:
    # nodeps[pth] extras
    import setuptools  # type: ignore[attr-defined]
    from setuptools.command.build_py import build_py  # type: ignore[attr-defined]
    from setuptools.command.develop import develop  # type: ignore[attr-defined]
    from setuptools.command.easy_install import easy_install  # type: ignore[attr-defined]
    from setuptools.command.install_lib import install_lib  # type: ignore[attr-defined]
except ModuleNotFoundError:
    setuptools = object
    build_py = object
    develop = object
    easy_install = object
    install_lib = object
# </editor-fold>


try:
    if "_in_process.py" not in sys.argv[0]:
        # Avoids failing when asking for build requirements and distutils.core is not available since pip patch it
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=UserWarning, message="Setuptools is replacing distutils.")

            # Must be imported after setuptools
            # noinspection PyCompatibility
            import pip._internal.cli.base_command
            import pip._internal.metadata
            import pip._internal.models.direct_url
            import pip._internal.models.scheme
            import pip._internal.operations.install.wheel
            import pip._internal.req.req_install
            import pip._internal.req.req_uninstall
except ModuleNotFoundError:
    pip = object


if TYPE_CHECKING:
    from urllib.parse import ParseResult
    from IPython.core.interactiveshell import InteractiveShell

    # noinspection PyCompatibility
    from pip._internal.cli.base_command import Command
    from traitlets.config import Config

LOGGER = logging.getLogger(__name__)

_NODEPS_PIP_POST_INSTALL = {}
"""Holds the context with wheels installed and paths to package installed to be used in post install"""


_KT = TypeVar("_KT")
_T = TypeVar("_T")
_VT = TypeVar("_VT")
P = ParamSpec("P")
T = TypeVar("T")

class TempDir(tempfile.TemporaryDirectory):
    """Wrapper for :class:`tempfile.TemporaryDirectory` that provides Path-like.

    Examples:
        >>> from nodeps import TempDir
        >>> from nodeps import MACOS
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


def _pip_base_command(self: Command, args: list[str]) -> int:
    """Post install pip patch."""
    try:
        log = ColorLogger.logger()
        with self.main_context():
            rv = self._main(args)
            if rv == 0 and self.__class__.__name__ == "InstallCommand":
                for key, value in _NODEPS_PIP_POST_INSTALL.items():
                    p = Project(key)
                    p.completions()
                    p.brew()
                    for file in findfile(NODEPS_PIP_POST_INSTALL_FILENAME, value):
                        log.info(self.__class__.__name__, extra={"extra": f"post install '{key}': {file}"})
                        exec_module_from_file(file)
            return rv
    finally:
        logging.shutdown()


def _pip_install_wheel(
    name: str,
    wheel_path: str,
    scheme: pip._internal.models.scheme.Scheme,
    req_description: str,
    pycompile: bool = True,
    warn_script_location: bool = True,
    direct_url: pip._internal.models.direct_url.DirectUrl | None = None,
    requested: bool = False,
):
    """Pip install wheel patch to post install."""
    with zipfile.ZipFile(wheel_path) as z, pip._internal.operations.install.wheel.req_error_context(req_description):
        pip._internal.operations.install.wheel._install_wheel(
            name=name,
            wheel_zip=z,
            wheel_path=wheel_path,
            scheme=scheme,
            pycompile=pycompile,
            warn_script_location=warn_script_location,
            direct_url=direct_url,
            requested=requested,
        )
        global _NODEPS_PIP_POST_INSTALL  # noqa: PLW0602
        _NODEPS_PIP_POST_INSTALL[name] = Path(scheme.purelib, name)


def _pip_uninstall_req(self, auto_confirm: bool = False, verbose: bool = False):
    """Pip uninstall patch to post install."""
    assert self.req  # noqa: S101
    p = Project(self.req.name)
    p.completions(uninstall=True)

    dist = pip._internal.metadata.get_default_environment().get_distribution(self.req.name)
    if not dist:
        pip._internal.req.req_install.logger.warning("Skipping %s as it is not installed.", self.name)
        return None
    pip._internal.req.req_install.logger.info("Found existing installation: %s", dist)
    uninstalled_pathset = pip._internal.req.req_uninstall.UninstallPathSet.from_dist(dist)
    uninstalled_pathset.remove(auto_confirm, verbose)
    return uninstalled_pathset


def _setuptools_build_quiet(self, importable) -> None:
    """Setuptools build py patch to quiet build."""
    if NODEPS_QUIET:
        return
    if importable not in self._already_warned:
        self._Warning.emit(importable=importable)
        self._already_warned.add(importable)


def ins(obj: Any, *, _console: Console | None = None, title: str | None = None, _help: bool = False,
        methods: bool = True, docs: bool = False, private: bool = True,
        dunder: bool = False, sort: bool = True, _all: bool = False, value: bool = True, ):
    """Wrapper :func:`rich.inspect` for :class:`rich._inspect.Inspect`.

    Changing defaults to: ``docs=False, methods=True, private=True``.

    Inspect any Python object.

    Examples:
        >>> from nodeps import ins
        >>>
        >>> # to see summarized info.
        >>> ins(ins)  # doctest: +SKIP
        >>> # to not see methods.
        >>> ins(ins, methods=False)  # doctest: +SKIP
        >>> # to see full (non-abbreviated) help.
        >>> ins(ins, help=True)  # doctest: +SKIP
        >>> # to not see private attributes (single underscore).
        >>> ins(ins, private=False)  # doctest: +SKIP
        >>> # to see attributes beginning with double underscore.
        >>> ins(ins, dunder=True)  # doctest: +SKIP
        >>> # to see all attributes.
        >>> ins(ins, _all=True)  # doctest: +SKIP
        '

    Args:
        obj (Any): An object to inspect.
        _console (Console, optional): Rich Console.
        title (str, optional): Title to display over inspect result, or None use type. Defaults to None.
        _help (bool, optional): Show full help text rather than just first paragraph. Defaults to False.
        methods (bool, optional): Enable inspection of callables. Defaults to False.
        docs (bool, optional): Also render doc strings. Defaults to True.
        private (bool, optional): Show private attributes (beginning with underscore). Defaults to False.
        dunder (bool, optional): Show attributes starting with double underscore. Defaults to False.
        sort (bool, optional): Sort attributes alphabetically. Defaults to True.
        _all (bool, optional): Show all attributes. Defaults to False.
        value (bool, optional): Pretty print value. Defaults to True.
    """
    rich.inspect(obj=obj, console=_console or CONSOLE, title=title, help=_help, methods=methods, docs=docs,
                 private=private, dunder=dunder, sort=sort, all=_all, value=value)


def load_ipython_extension1(  # noqa: PLR0912, PLR0915
    ipython: InteractiveShell | None = None, magic: bool = False
) -> Config | None:
    """IPython extension.

    We are entering twice at startup: from $PYTHONSTARTUP and ipython is None
        and from $IPYTHONDIR to load nodeps extension.

    The `ipython` argument is the currently active `InteractiveShell`
    instance, which can be used in any way. This allows you to register
    new magics or aliases, for example.

    https://ipython.readthedocs.io/en/stable/config/extensions/index.html

    Before extension is loaded:
        - almost no globals
        - and only nodeps in sys.modules
    """
    if ipython:
        config = ipython.config
        ipython.prompts = MyPrompt(ipython)

        if NODEPS_PROJECT_NAME not in sys.modules:
            imported = importlib.import_module(NODEPS_PROJECT_NAME)
        module = None

        ipython.ex("'%autoreload 2'")
        ipython.extension_manager.shell.run_line_magic("autoreload", "3")
        if module != NODEPS_PROJECT_NAME:
            ipython.ex(f"import {NODEPS_PROJECT_NAME}")
        # rich.pretty.install(CONSOLE, expand_all=True)
    else:
        try:
            config = get_config()  # type: ignore[attr-defined]
        except NameError:
            from traitlets.config import Config

            config = Config()


    config.InteractiveShellApp.exec_lines = [f"import {NODEPS_PROJECT_NAME}"]
    if not from_pycharm_console and not magic:  # debug in console goes thu Prompt
        config.TerminalInteractiveShell.prompts_class = MyPrompt

    if ipython is None:
        return config
    return None



if "pip._internal.operations.install.wheel" in sys.modules:
    pip._internal.operations.install.wheel.install_wheel = _pip_install_wheel
    pip._internal.cli.base_command.Command.main = _pip_base_command
    pip._internal.req.req_install.InstallRequirement.uninstall = _pip_uninstall_req


if "setuptools.command.build_py" in sys.modules:
    setuptools.command.build_py._IncludePackageDataAbuse.warn = _setuptools_build_quiet

is_repl(syspath=True)
