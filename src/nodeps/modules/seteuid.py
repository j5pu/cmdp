"""Seteuid module."""
from __future__ import annotations

__all__ = (
    "root",
)

import builtins
import contextlib
import os
import sys
from typing import TYPE_CHECKING, ParamSpec, TypeVar

from nodeps.modules.path import Path

if TYPE_CHECKING:
    from collections.abc import Callable

SETEUID = False
"""Allow to change seteuid. Changes the owner of executable to root so updates will not work."""
EUID = os.geteuid()
UID = os.getuid()
builtins.euid = EUID
builtins.uid = UID

P = ParamSpec("P")
T = TypeVar("T")

if SETEUID:
    try:
        os.seteuid(0)
    except PermissionError:
        if not Path.setid_executable_is():
            # ADVERTENCIA: changes the owner of executable to root so updates will not work
            Path.setid_executable()
            # Relaunch to take effect
            os.execvp(sys.argv[0], sys.argv[1:])  # noqa: S606
    finally:
        os.seteuid(EUID)


@contextlib.contextmanager
def root(func: Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> T:
    """Runs function with  euid set to 0."""
    if not SETEUID:
        msg = f"{root.__qualname__} is not enabled: {SETEUID=}"
        raise RuntimeError(msg)

    try:
        os.seteuid(0)
        return func(*args, **kwargs)
    finally:
        os.seteuid(EUID)
