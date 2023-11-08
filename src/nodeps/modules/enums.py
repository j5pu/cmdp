"""Enums Module."""
__all__ = (
    "Bump",
    "ProjectRepos",
)

import enum


class Bump(str, enum.Enum):
    """Bump class."""
    MAJOR = "MAJOR"
    MINOR = "MINOR"
    PATCH = "PATCH"


class ProjectRepos(str, enum.Enum):
    """Options to show repos in Project class."""

    DICT = enum.auto()
    INSTANCES = enum.auto()
    NAMES = enum.auto()
    PATHS = enum.auto()
    PY = enum.auto()
