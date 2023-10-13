"""NoDeps Extras Module."""
from . import _ansi, _echo, _log, _pickle, _pretty, _repo, _url
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
    CONSOLE,
    FORCE_COLOR,
    IPYTHON,
    IS_REPL,
    IS_TTY,
    OpenIO,
    ic,
    icc,
    ins,
    is_terminal,
    print_json,
)
from ._repo import Repo
from ._url import (
    PYTHON_FTP,
    python_latest,
    python_version,
    python_versions,
    request_x_api_key_json,
)

__all__ = (
        _ansi.__all__ +
        _echo.__all__ +
        _log.__all__ +
        _pickle.__all__ +
        _pretty.__all__ +
        _repo.__all__ +
        _url.__all__
)
