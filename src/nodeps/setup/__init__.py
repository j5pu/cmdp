"""Setuptools Pth and Pip Post Install Module."""
from __future__ import annotations

__all__ = (
    "BuildPy",
    "Develop",
    "EasyInstall",
    "InstallLib",
)

import filecmp
import itertools
import logging
import sys
import warnings
import zipfile
from contextvars import ContextVar
from typing import TYPE_CHECKING

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

from ..modules import NODEPS_PIP_POST_INSTALL_FILENAME, ColorLogger, Path, Project, exec_module_from_file, findfile

if TYPE_CHECKING:
    # noinspection PyCompatibility
    from pip._internal.cli.base_command import Command

_NODEPS_PIP_POST_INSTALL = {}
"""Holds the context with wheels installed and paths to package installed to be used in post install"""


class BuildPy(build_py):
    """Build py with pth files installed."""

    def run(self):
        """Run build py."""
        super().run()
        self.outputs = []
        self.outputs = _copy_pths(self, self.build_lib)

    def get_outputs(self, include_bytecode=1):
        """Get outputs."""
        return itertools.chain(build_py.get_outputs(self, 0), self.outputs)


class Develop(develop):
    """PTH Develop Install."""

    def run(self):
        """Run develop."""
        super().run()
        _copy_pths(self, self.install_dir)


class EasyInstall(easy_install):
    """PTH Easy Install."""

    def run(self, *args, **kwargs):
        """Run easy install."""
        super().run(*args, **kwargs)
        _copy_pths(self, self.install_dir)


class InstallLib(install_lib):
    """PTH Install Library."""

    def run(self):
        """Run Install Library."""
        super().run()
        self.outputs = []
        self.outputs = _copy_pths(self, self.install_dir)

    def get_outputs(self):
        """Get outputs."""
        return itertools.chain(install_lib.get_outputs(self), self.outputs)


def _copy_pths(self: BuildPy | Develop | EasyInstall | InstallLib, directory: str) -> list[str]:
    log = ColorLogger.logger()
    outputs = []
    data = self.get_outputs() if isinstance(self, (BuildPy | InstallLib)) else self.outputs
    for source in data:
        if source.endswith(".pth"):
            destination = Path(directory, Path(source).name)
            if not destination.is_file() or not filecmp.cmp(source, destination):
                destination = str(destination)
                msg = f"{self.__class__.__name__}: {str(Path(sys.executable).resolve())[-4:]}"
                log.info(
                    msg,
                    extra={"extra": f"{source} -> {destination}"},
                )
                self.copy_file(source, destination)
                outputs.append(destination)
    return outputs


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
    if ContextVar('NODEPS_QUIET') is True:
        return
    if importable not in self._already_warned:
        self._Warning.emit(importable=importable)
        self._already_warned.add(importable)


if "pip._internal.operations.install.wheel" in sys.modules:
    pip._internal.operations.install.wheel.install_wheel = _pip_install_wheel
    pip._internal.cli.base_command.Command.main = _pip_base_command
    pip._internal.req.req_install.InstallRequirement.uninstall = _pip_uninstall_req

if "setuptools.command.build_py" in sys.modules:
    setuptools.command.build_py._IncludePackageDataAbuse.warn = _setuptools_build_quiet
