"""NoDeps Extras Module."""
__all__ = (
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
)

from ._ansi import getstdout, strip
from ._echo import (
    COLORIZE,
    SYMBOL,
    Color,
    EnumLower,
    Symbol,
    bblack,
    bblue,
    bcyan,
    bgreen,
    black,
    blue,
    bmagenta,
    bred,
    bwhite,
    byellow,
    cyan,
    green,
    magenta,
    red,
    reset,
    white,
    yellow,
)
from ._log import LOGGER_DEFAULT_FMT, logger
from ._pickle import cache
from ._pretty import (
    ic,
    icc,
)
from ._repo import Repo
from ._url import (
    PYTHON_FTP,
    python_latest,
    python_version,
    python_versions,
    request_x_api_key_json,
)
