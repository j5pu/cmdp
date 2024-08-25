"""Import all for module.

Caveats:
    IPYTHON not available in IPython only in PyCharm
"""  # noqa: INP001

from nodeps.ipython_variables import NODEPS_IPYTHON_IMPORT_MODULE

if NODEPS_IPYTHON_IMPORT_MODULE:
    exec(f"from {NODEPS_IPYTHON_IMPORT_MODULE} import *")  # noqa: S102
