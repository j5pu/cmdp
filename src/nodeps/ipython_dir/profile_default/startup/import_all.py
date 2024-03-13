"""Import all for module.

Caveats:
    IPYTHON not available in IPython only in PyCharm
"""  # noqa: INP001

try:
    from IPython.core.getipython import get_ipython  # type: ignore[attr-defined]
except ModuleNotFoundError:
    get_ipython = lambda *args: None  # noqa: E731

from nodeps.ipython_dir.profile_default.ipython_config import NODEPS_IPYTHON_IMPORT_MODULE

if NODEPS_IPYTHON_IMPORT_MODULE:
    exec(f"from {NODEPS_IPYTHON_IMPORT_MODULE} import *")  # noqa: S102
