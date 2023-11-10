"""NoDeps Helpers and Utils Module."""
import os

from . import extras, ipython, modules
from .extras import *
from .ipython import *
from .modules import *

os.environ["PIP_ROOT_USER_ACTION"] = "ignore"
os.environ["PY_IGNORE_IMPORTMISMATCH"] = "1"
os.environ["PYTHONDONTWRITEBYTECODE"] = ""

__all__ = extras.__all__ + ipython.__all__ + modules.__all__
