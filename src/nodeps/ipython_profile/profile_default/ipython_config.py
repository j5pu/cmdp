"""IPython Config."""  # noqa: INP001
from nodeps import IPYTHON_EXTENSIONS

config = get_config()  # type: ignore[attr-defined]  # noqa: F821
config.TerminalInteractiveShell.banner1 = ""
config.TerminalIPythonApp.extensions = IPYTHON_EXTENSIONS
