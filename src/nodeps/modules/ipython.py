"""IPython Module."""
__all__ = (
    "load_ipython_extension",
)

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


def load_ipython_extension():
    pass