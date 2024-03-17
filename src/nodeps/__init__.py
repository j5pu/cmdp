"""NoDeps Helpers and Utils Module."""
import os  # noqa: I001

from . import extras, ipython_variables, modules, setup
from .extras import *
from .ipython_variables import *
from .modules import *
from .setup import *
from .ipython_dir.profile_default import ipython_pycharm_startup  # DON'T REMOVE  # noqa: F401

os.environ["IPYTHONDIR"] = str(IPYTHONDIR)  # noqa: F405
os.environ["PIP_ROOT_USER_ACTION"] = "ignore"
os.environ["PY_IGNORE_IMPORTMISMATCH"] = "1"
os.environ["PYTHONDONTWRITEBYTECODE"] = ""
os.environ["PYTHONSTARTUP"] = str(PYTHONSTARTUP)  # noqa: F405

__all__ = extras.__all__ + ipython_variables.__all__ + modules.__all__ + setup.__all__
