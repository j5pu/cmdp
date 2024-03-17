"""IPython PYCharm IPython startup after client is available module.

Needs to be imported in nodeps.__init__ and only works from nodeps in PyCharm
"""  # noqa: INP001
import sys

from nodeps.ipython_variables import (
    IPYTHON_EXTENSIONS,
    IPYTHON_STARTUP_IPY_FILES,
    IPYTHON_STARTUP_PY_FILES,
    IPYTHONType,
    PYCHARM_CONSOLE,
)

PYCHARM_IMPORTS_PYTHON_CONFIG = "do_import" in sys._getframe(8).f_code.co_name
"""Variable to check that PyCharm IPython is not broken and imports ipython_config with IPYTHON."""

try:
    from IPython.core.getipython import get_ipython  # type: ignore[attr-defined]
except ModuleNotFoundError:
    get_ipython = lambda *args: None  # noqa: E731

IPYTHON: IPYTHONType = get_ipython()
if IPYTHON:
    if PYCHARM_CONSOLE and PYCHARM_IMPORTS_PYTHON_CONFIG:
        print(f"{PYCHARM_IMPORTS_PYTHON_CONFIG=}", file=sys.stderr)
    for file in IPYTHON_STARTUP_IPY_FILES:
        IPYTHON.safe_execfile_ipy(str(file), IPYTHON.user_ns, raise_exceptions=True)
    for file in IPYTHON_STARTUP_PY_FILES:
        IPYTHON.safe_execfile(str(file), IPYTHON.user_ns, raise_exceptions=True)
    for extension in IPYTHON_EXTENSIONS:
        if extension not in IPYTHON.extension_manager.loaded:
            IPYTHON.extension_manager.load_extension(extension)
    loaded = IPYTHON.extension_manager.loaded
    IPYTHON.ex(f"_extensions_loaded = {loaded}")
