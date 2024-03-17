import importlib
import os
import pathlib
import sys

import pytest

import nodeps.modules.constants
import nodeps.ipython_dir
import nodeps.ipython_dir.extensions
import nodeps.ipython_dir.profile_default
import nodeps.ipython_dir.profile_default.ipython_config
import nodeps.ipython_dir.profile_default.startup
from nodeps import EXECUTABLE
from nodeps import EXECUTABLE_SITE
from nodeps import in_tox
from nodeps import IPYTHON_CONFIG_FILE
from nodeps import IPYTHON_EXTENSIONS
from nodeps import IPYTHON_EXTENSIONS_DIR
from nodeps import IPYTHON_EXTENSIONS_NODEPS
from nodeps import IPYTHON_PROFILE_DEFAULT_DIR
from nodeps import IPYTHON_STARTUP_DIR
from nodeps import IPYTHON_STARTUP_IPY_FILES
from nodeps import IPYTHON_STARTUP_PY_FILES
from nodeps import IPYTHONDIR
from nodeps import NODEPS_MODULE_PATH
from nodeps import NODEPS_PROJECT_NAME
from nodeps import NODEPS_SRC
from nodeps import NODEPS_TOP
from nodeps import Path
from nodeps import PYTHONSTARTUP
from nodeps import RUNNING_IN_VENV
from nodeps import VIRTUAL_ENV
from nodeps import VIRTUAL_ENV_CWD_STARTUP
from nodeps import VIRTUAL_ENV_SRC

_NODEPS_NAME = "nodeps"
_PURELIB = Path.purelib()
_SYS_PREFIX_PATH = Path(sys.prefix)
_SYS_BASE_PREFIX_PATH = Path(sys.base_prefix)
_IN_TOX = in_tox()


@pytest.mark.skipif(_IN_TOX is True, reason='running in tox')
def test_nodeps_paths():
    assert NODEPS_MODULE_PATH.name == _NODEPS_NAME
    assert NODEPS_PROJECT_NAME == _NODEPS_NAME
    assert NODEPS_SRC.name == "src"


@pytest.mark.skipif(_IN_TOX is True, reason='running in tox')
def test_constants_venv():
    if RUNNING_IN_VENV:
        assert EXECUTABLE != EXECUTABLE_SITE
        assert _SYS_PREFIX_PATH != _SYS_BASE_PREFIX_PATH
        assert NODEPS_TOP == NODEPS_SRC.parent
        assert NODEPS_SRC == VIRTUAL_ENV_SRC
        assert RUNNING_IN_VENV is True
        assert VIRTUAL_ENV is not None
        assert VIRTUAL_ENV.is_dir()
        assert VIRTUAL_ENV_CWD_STARTUP.is_dir()
        assert VIRTUAL_ENV_SRC.is_dir()
        assert VIRTUAL_ENV_SRC.name == "src"
    else:
        assert _SYS_PREFIX_PATH == _SYS_BASE_PREFIX_PATH
        assert VIRTUAL_ENV is None
        assert VIRTUAL_ENV_CWD_STARTUP is None
        assert VIRTUAL_ENV_SRC is None


def test_ipython_paths():
    assert IPYTHONDIR == pathlib.Path(nodeps.ipython_dir.__path__[0])
    assert IPYTHON_PROFILE_DEFAULT_DIR == pathlib.Path(nodeps.ipython_dir.profile_default.__path__[0])
    assert IPYTHON_EXTENSIONS_DIR == pathlib.Path(nodeps.ipython_dir.extensions.__path__[0])
    assert IPYTHON_STARTUP_DIR == pathlib.Path(nodeps.ipython_dir.profile_default.startup.__path__[0])
    assert os.environ["IPYTHONDIR"] == str(IPYTHONDIR)
    assert IPYTHON_CONFIG_FILE == pathlib.Path(nodeps.ipython_dir.profile_default.ipython_config.__file__)
    assert IPYTHON_CONFIG_FILE.is_file()
    assert PYTHONSTARTUP.is_file()
    assert len(IPYTHON_STARTUP_IPY_FILES) >= 1
    assert len(IPYTHON_STARTUP_PY_FILES) >= 1


def test_ipython_imports():
    assert len(IPYTHON_EXTENSIONS_NODEPS) >= 1
    for i in IPYTHON_EXTENSIONS_NODEPS:
        rv = importlib.import_module(i)
        assert rv.__name__ == i
        assert rv.__name__ in IPYTHON_EXTENSIONS


@pytest.mark.skipif(_IN_TOX is True, reason='running in tox')
def test_sys_path():
    assert str(NODEPS_SRC) in sys.path
    if RUNNING_IN_VENV:
        assert str(VIRTUAL_ENV_CWD_STARTUP) in sys.path
        assert str(VIRTUAL_ENV_SRC) in sys.path
    else:
        assert str(VIRTUAL_ENV_CWD_STARTUP) not in sys.path
        assert str(VIRTUAL_ENV_SRC) not in sys.path
