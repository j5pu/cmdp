"""PTH file support for nodeps.

Note: This module can not be imported in __init__,py for compatibility with pip distutils
"""
__all__ = ()
import filecmp
import itertools
from pathlib import Path

from setuptools.command.install_lib import install_lib  # type: ignore[attr-defined]

from color_logger import ColorLogger


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


def _copy_pths(self: InstallLib,
               directory: str) -> list[str]:
    log = ColorLogger.logger(__name__)
    outputs = []
    data = self.get_outputs() if isinstance(self, InstallLib) else self.outputs
    for source in data:
        if source.endswith(".pth"):
            destination = Path(directory, Path(source).name)
            if not destination.is_file() or not filecmp.cmp(source, destination):
                destination = str(destination)
                log.info(self.__class__.__name__, extra={"extra": f"{source} -> {destination}"})
                self.copy_file(source, destination)
                outputs.append(destination)
    return outputs
