"""NoDeps Helpers and Utils Module."""
__all__ = (
    "EXECUTABLE",
    "EXECUTABLE_SITE",
    "LINUX",
    "MACOS",
    "PW_ROOT",
    "PW_USER",
    "USER",
    "TempDir",
    "ami",
)

import getpass
import os
import pwd
import sys
import tempfile
from pathlib import Path
from typing import ParamSpec, TypeVar

EXECUTABLE = Path(sys.executable)
EXECUTABLE_SITE = Path(EXECUTABLE).resolve()
LINUX = sys.platform == "linux"
"""Is Linux? sys.platform == 'linux'"""
MACOS = sys.platform == "darwin"
"""Is macOS? sys.platform == 'darwin'"""
PW_ROOT = pwd.getpwnam("root")
PW_USER = pwd.getpwnam(os.environ["USER"])
USER = os.getenv("USER")
""""Environment Variable $USER"""

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


def ami(user: str = "root") -> bool:
    """Check if Current User is User in Argument (default: root).

    Examples:
        >>> from nodeps import ami
        >>> from nodeps import USER
        >>>
        >>> ami(USER)
        True
        >>> ami()
        False

    Arguments:
        user: to check against current user (Default: False)

    Returns:
        CompletedProcess if the current user is not the same as user, None otherwise
    """
    return os.getuid() == pwd.getpwnam(user or getpass.getuser()).pw_uid
