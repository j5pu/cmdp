"""NoDeps Helpers and Utils Module."""
import os  # noqa: I001

# DO NOT SORT IMPORTS OTHERWISE NOT ALL GET IMPORTED.
from . import extras, modules, setup
from .extras import *
from .ipython_dir.profile_default.ipython_config import *
from .modules import *
from .setup import *
from .ipython_dir.profile_default import (
    ipython_pycharm_startup,  # DON'T REMOVE NEEDED BY PYCHARM IPython do_import with client  # noqa: F401
    ipython_config,
)

os.environ["IPYTHONDIR"] = str(IPYTHONDIR)  # noqa: F405
os.environ["PIP_ROOT_USER_ACTION"] = "ignore"
os.environ["PY_IGNORE_IMPORTMISMATCH"] = "1"
os.environ["PYTHONDONTWRITEBYTECODE"] = ""
os.environ["PYTHONSTARTUP"] = str(PYTHONSTARTUP)  # noqa: F405

__all__ = extras.__all__ + ipython_config.__all__ + modules.__all__ + setup.__all__
