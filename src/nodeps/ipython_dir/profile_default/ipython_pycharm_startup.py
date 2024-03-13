"""IPython PYCharm IPython startup after client is available module.

Needs to be imported in nodeps.__init__
"""  # noqa: INP001
import pathlib
import sys

if (_path := str(pathlib.Path(__file__).parent)) not in sys.path:
    sys.path.insert(0, _path)

from ipython_config import (
    IPYTHON,
    IPYTHON_EXTENSIONS,
    IPYTHON_STARTUP_IPY_FILES,
    IPYTHON_STARTUP_PY_FILES,
    PYCHARM_CONSOLE,
)

PYCHARM_IMPORTS_PYTHON_CONFIG = "do_import" in sys._getframe(8).f_code.co_name
"""Variable to check that PyCharm IPython is not broken and imports ipython_config with IPYTHON."""

if PYCHARM_CONSOLE:
    print(f"{PYCHARM_IMPORTS_PYTHON_CONFIG=}", file=sys.stderr)

if IPYTHON:
    for file in IPYTHON_STARTUP_IPY_FILES:
        IPYTHON.safe_execfile_ipy(str(file), IPYTHON.user_ns)
    for file in IPYTHON_STARTUP_PY_FILES:
        IPYTHON.safe_execfile(str(file), IPYTHON.user_ns)
    for extension in IPYTHON_EXTENSIONS:
        if extension not in IPYTHON.extension_manager.loaded:
            IPYTHON.extension_manager.load_extension(extension)
