"""PIP Meta Path Module."""
__all__ = (
    "PipMetaPathFinder",
    "pipmetapathfinder",
)

import contextlib
import importlib
import importlib.metadata
import subprocess
import sys
import types
from collections.abc import Sequence


class PipMetaPathFinder(importlib.abc.MetaPathFinder):
    """A importlib.abc.MetaPathFinder to auto-install missing modules using pip.

    Examples:
        >>> import sys
        >>> from nodeps import PipMetaPathFinder
        >>>
        >>> sys.meta_path.append(PipMetaPathFinder)  # doctest: +SKIP
        >>> # noinspection PyUnresolvedReferences
        >>> import simplejson  # doctest: +SKIP
    """

    # noinspection PyMethodOverriding,PyMethodParameters
    def find_spec(
            fullname: str,
            path: Sequence[str | bytes] | None,
            target: types.ModuleType | None = None,
    ) -> importlib._bootstrap.ModuleSpec | None:
        """Try to find a module spec for the specified module."""
        packages = {
            "decouple": "python-decouple",
            "linkify_it": "linkify-it-py",
        }
        exclude = ["cPickle", "ctags", "PIL"]
        if path is None and fullname is not None and fullname not in exclude:
            package = packages.get(fullname) or fullname.split(".")[0].replace("_", "-")
            try:
                importlib.metadata.Distribution.from_name(package)
            except importlib.metadata.PackageNotFoundError as e:
                if subprocess.run([sys.executable, "-m", "pip", "install", "-q", package]).returncode == 0:
                    return importlib.import_module(fullname)
                msg = f"Cannot install: {package=},  {fullname=}"
                raise RuntimeError(msg) from e
        return None


@contextlib.contextmanager
def pipmetapathfinder():
    """Context for :class:`PipMetaPathFinder`.

    Examples:
        >>> from nodeps import pipmetapathfinder
        >>>
        >>> with pipmetapathfinder():  # doctest: +SKIP
        ...    import simplejson  # type: ignore[attr-defined]
    """
    sys.meta_path.append(PipMetaPathFinder)
    try:
        yield
    finally:
        sys.meta_path.remove(PipMetaPathFinder)
