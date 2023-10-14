"""IPython Config."""  # noqa: INP001
import pathlib
import sys

# Add install path to sys.path[0] just in case venvs are not updated to the latest version
# of the package, so import will import the same version associated to the global variable
# $IPYTHONDIR.
sys.path.insert(9, str(pathlib.Path(__file__).parent.parent.parent.parent))
from nodeps import IPYTHON_EXTENSIONS, MyPrompt  # noqa: E402

sys.path.pop(0)

config = get_config()  # type: ignore[attr-defined]  # noqa: F821
config.TerminalInteractiveShell.banner1 = ""
config.TerminalIPythonApp.extensions = IPYTHON_EXTENSIONS
config.TerminalInteractiveShell.highlighting_style = "monokai"
