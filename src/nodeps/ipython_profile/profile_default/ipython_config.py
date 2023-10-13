"""IPython Config."""  # noqa: INP001
from nodeps import IPYTHON_EXTENSIONS, MyPrompt

config = get_config()  # type: ignore[attr-defined]  # noqa: F821
config.TerminalInteractiveShell.banner1 = ""
config.TerminalIPythonApp.extensions = IPYTHON_EXTENSIONS
config.TerminalInteractiveShell.highlighting_style = "monokai"
