"""IPython Module."""
__all__ = (
    "load_ipython_extension",
)

import contextlib

try:
    from IPython.core.application import BaseIPythonApplication  # type: ignore[attr-defined]
    from IPython.core.formatters import PlainTextFormatter  # type: ignore[attr-defined]
    from IPython.core.interactiveshell import InteractiveShell  # type: ignore[attr-defined]
    from IPython.core.shellapp import InteractiveShellApp  # type: ignore[attr-defined]
    from IPython.terminal.interactiveshell import TerminalInteractiveShell  # type: ignore[attr-defined]
    from IPython.terminal.ipapp import TerminalIPythonApp  # type: ignore[attr-defined]
    from IPython.terminal.prompts import Prompts, Token  # type: ignore[attr-defined]
except ModuleNotFoundError:
    Prompts = Token = object


def load_ipython_extension(ipython: InteractiveShell | None = None, magic: bool = False):
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
    if ipython is None:
        with contextlib.suppress(NameError):
            ipython: InteractiveShell = get_ipython()  # type: ignore[attr-defined]  # noqa: F821
