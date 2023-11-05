"""IPython Config."""  # noqa: INP001

from nodeps import IPYTHON_EXTENSIONS, NODEPS_PROJECT_NAME

try:
    ipython = get_ipython()  # type: ignore[attr-defined]
    config = ipython.config
except NameError:
    config = get_config()  # noqa: F821

config.InteractiveShell.banner1 = ""
config.TerminalInteractiveShell.banner1 = ""
config.TerminalIPythonApp.extensions = IPYTHON_EXTENSIONS
# config.TerminalInteractiveShell.highlighting_style = "monokai"
