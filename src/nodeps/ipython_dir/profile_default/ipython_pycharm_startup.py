"""IPython PYCharm IPython startup after client is available module.

Needs to be imported in nodeps.__init__ and only works from nodeps in PyCharm
"""  # noqa: INP001

from nodeps.ipython_variables import (
    IPYTHON_EXTENSIONS,
    IPYTHON_STARTUP_IPY_FILES,
    IPYTHON_STARTUP_PY_FILES,
    IPYTHONType,
)

try:
    # noinspection PyUnboundLocalVariable
    ipy: IPYTHONType = get_ipython()  # type: ignore[attr-defined]
except NameError:
    try:
        from IPython.core.getipython import get_ipython  # type: ignore[attr-defined]
    except ModuleNotFoundError:
        get_ipython = lambda *args: None  # noqa: E731
    ipy: IPYTHONType = get_ipython()

if ipy is not None:
    for file in IPYTHON_STARTUP_IPY_FILES:
        ipy.safe_execfile_ipy(str(file), ipy.user_ns, raise_exceptions=True)
    for file in IPYTHON_STARTUP_PY_FILES:
        ipy.safe_execfile(str(file), ipy.user_ns, raise_exceptions=True)
    for extension in IPYTHON_EXTENSIONS:
        if extension not in ipy.extension_manager.loaded:
            ipy.extension_manager.load_extension(extension)
    loaded = ipy.extension_manager.loaded
    ipy.ex(f"_extensions_loaded = {loaded}")
