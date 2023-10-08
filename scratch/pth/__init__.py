"""PTH file support for nodeps.

Note: This module can not be imported in __init__,py for compatibility with pip distutils
"""
__all__ = ()
import filecmp
import itertools
from pathlib import Path

import _distutils_hack

from color_logger import ColorLogger

_distutils_hack.ensure_local_distutils()

try:
    # nodeps[pth] extras
    from setuptools.command.build_py import build_py  # type: ignore[attr-defined]
    from setuptools.command.develop import develop  # type: ignore[attr-defined]
    from setuptools.command.easy_install import easy_install  # type: ignore[attr-defined]
    from setuptools.command.install_lib import install_lib  # type: ignore[attr-defined]
except ModuleNotFoundError:
    build_py = object
    develop = object
    easy_install = object
    install_lib = object


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


def _copy_pths(self: BuildPy | Develop | EasyInstall | InstallLib,
               directory: str) -> list[str]:
    log = ColorLogger.logger(__name__)
    outputs = []
    data = self.get_outputs() if isinstance(self, (BuildPy | InstallLib)) else self.outputs
    for source in data:
        if source.endswith(".pth"):
            destination = Path(directory, Path(source).name)
            if not destination.is_file() or not filecmp.cmp(source, destination):
                destination = str(destination)
                log.info(self.__class__.__name__, extra={"extra": f"{source} -> {destination}"})
                self.copy_file(source, destination)
                outputs.append(destination)
    return outputs
