"""IPython variables module."""  # noqa: INP001
__all__ = (
    "IPYTHONType",
    "CWD_STARTUP",
    "CWD_SRC",
    "IPYTHON_PROFILE_DEFAULT_DIR",
    "IPYTHON",
    "IPYTHONDIR",
    "NODEPS_MODULE_PATH",
    "NODEPS_NAME",
    "NODEPS_SRC",
    "VIRTUAL_ENV",
    "VIRTUAL_ENV_CWD_STARTUP",
    "VIRTUAL_ENV_SRC",
    "IPYTHON_CONFIG_FILE",
    "IPYTHON_EXTENSIONS_DIR",
    "IPYTHON_EXTENSIONS_NODEPS",
    "IPYTHON_EXTENSIONS",
    "IPYTHON_STARTUP_DIR",
    "IPYTHON_STARTUP_IPY_FILES",
    "IPYTHON_STARTUP_PY_FILES",
    "PYTHONSTARTUP",
    "RELOAD_EXTENSION",
    "PYCHARM_CONSOLE",
    "NODEPS_IPYTHON_IMPORT_MODULE",
)

import contextlib
import os
import pathlib
import platform
import sys
import tomllib
import warnings
from typing import TYPE_CHECKING, TypeAlias

try:
    # nodeps[ipython] extras
    import IPython.core.shellapp  # type: ignore[attr-defined]
    from IPython.core.getipython import get_ipython  # type: ignore[attr-defined]
    from IPython.core.interactiveshell import PickleShareDB  # type: ignore[attr-defined]
    from IPython.extensions.autoreload import update_instances  # type: ignore[attr-defined]
    from IPython.extensions.storemagic import refresh_variables  # type: ignore[attr-defined]
    from IPython.terminal.interactiveshell import TerminalInteractiveShell  # type: ignore[attr-defined]
    from IPython.terminal.prompts import Prompts, Token  # type: ignore[attr-defined]
    from traitlets.config.application import get_config  # type: ignore[attr-defined]  # type: ignore[attr-defined]
except ModuleNotFoundError:
    IPython = PickleShareDB = TerminalInteractiveShell = None
    Prompts = Token = object
    get_config = get_ipython = refresh_variables = update_instances = lambda *args: None

try:
    import _pydev_bundle.pydev_ipython_console_011  # type: ignore[attr-defined]
    from _pydev_bundle.pydev_ipython_console_011 import PyDevTerminalInteractiveShell  # type: ignore[attr-defined]
except ModuleNotFoundError:
    _pydev_bundle = PyDevTerminalInteractiveShell = object

# <editor-fold desc="Variables">
IPYTHONType: TypeAlias = TerminalInteractiveShell | PyDevTerminalInteractiveShell

CWD_STARTUP = pathlib.Path.cwd()
"""Startup CWD."""
CWD_SRC = _cwd_src if (_cwd_src := CWD_STARTUP / "src").is_dir() else None
"""CWD/src"""
IPYTHON_PROFILE_DEFAULT_DIR = pathlib.Path(__file__).parent
IPYTHON: TerminalInteractiveShell | PyDevTerminalInteractiveShell = get_ipython()
IPYTHONDIR = IPYTHON_PROFILE_DEFAULT_DIR.parent
"""IPython Profile: `export IPYTHONDIR="$(ipythondir)"`."""
NODEPS_MODULE_PATH = IPYTHONDIR.parent
"""NoDeps Source Path: src/nodeps or site-packages/nodeps"""
NODEPS_NAME = NODEPS_MODULE_PATH.name
NODEPS_SRC = NODEPS_MODULE_PATH.parent
"""Nodeps src directory /src or /site-packages for sys.path."""
VIRTUAL_ENV = pathlib.Path(_virtual_env) if (_virtual_env := os.environ.get("VIRTUAL_ENV")) else None
"""Virtual Env path."""
VIRTUAL_ENV_CWD_STARTUP = CWD_STARTUP if VIRTUAL_ENV else None
"""CWD if working in a virtual env."""
# noinspection PyUnboundLocalVariable
VIRTUAL_ENV_SRC = _src if VIRTUAL_ENV and (_src := VIRTUAL_ENV.parent / "src").is_dir() else None
"""src directory in a virtual env."""

IPYTHON_CONFIG_FILE = pathlib.Path(__file__)
IPYTHON_EXTENSIONS_DIR = IPYTHONDIR / "extensions"
"""Directory to install extensions, loaded automatically with ipython
if defined in config.InteractiveShellApp.extensions or
IPython.core.shellapp.InteractiveShellApp.extensions = IPYTHON_EXTENSIONS"""
IPYTHON_EXTENSIONS_NODEPS = [
    str(_i.relative_to(NODEPS_SRC)).replace("/", ".").replace(".py", "")
    for _i in IPYTHON_EXTENSIONS_DIR.iterdir() if _i.suffix == ".py"
]
"""Nodeps extensions module names installed in extensions dir."""
IPYTHON_EXTENSIONS = [
    "IPython.extensions.autoreload", "IPython.extensions.storemagic", "rich", *IPYTHON_EXTENSIONS_NODEPS
]
"""All IPython extensions to load, loaded automatically with ipython
if defined in config.InteractiveShellApp.extensions or
IPython.core.shellapp.InteractiveShellApp.extensions = IPYTHON_EXTENSIONS"""
IPYTHON_STARTUP_DIR = IPYTHON_PROFILE_DEFAULT_DIR / "startup"
""".py and .ipy files in this directory will be run *prior* to any code or files specified
via the exec_lines or exec_files configurables whenever you load this profile.
"""
IPYTHON_STARTUP_IPY_FILES = [_i for _i in IPYTHON_STARTUP_DIR.iterdir() if _i.suffix == ".ipy"]
""".ipy run prior to any code or files specified via exec_lines, run automatically by ipython."""
IPYTHON_STARTUP_PY_FILES = [_i for _i in IPYTHON_STARTUP_DIR.iterdir() if _i.suffix == ".py"]
""".py run prior to any code or files specified via exec_lines, run automatically by ipython."""
PYTHONSTARTUP = IPYTHON_PROFILE_DEFAULT_DIR / "python_startup.py"
"""Python Startup :mod:`python_startup.__init__`: `export PYTHONSTARTUP="$(pythonstartup)"`."""

PYCHARM_CONSOLE = None
"""Running in PyCharm console."""
for item in sys.path:
    if "PyCharm" in item or "pycharm" in item or "pydev" in item:
        PYCHARM_CONSOLE = True
        break

RELOAD_EXTENSION = None
"""Reload extension module name."""
for extension in IPYTHON_EXTENSIONS_NODEPS:
    if "reload" in extension:
        RELOAD_EXTENSION = extension
        break

NODEPS_IPYTHON_IMPORT_MODULE = None
"""Module to import all."""
if VIRTUAL_ENV:
    top = VIRTUAL_ENV.parent
    if (pyproject_toml := (top / "pyproject.toml")).is_file():
        with pathlib.Path(pyproject_toml).open("rb") as f:
            data = tomllib.load(f)
            NODEPS_IPYTHON_IMPORT_MODULE = data["project"]["name"]
    elif VIRTUAL_ENV_SRC:
        # src but not pyproject.toml
        NODEPS_IPYTHON_IMPORT_MODULE = VIRTUAL_ENV_SRC.parent.name
    elif (package := (top / top.name)).is_dir() and (package / "__init__.py").is_file():
        # no src but package/package/__init__.py
        NODEPS_IPYTHON_IMPORT_MODULE = top.name


# </editor-fold>

# <editor-fold desc="MyPrompt">
class MyPrompt(Prompts):
    """IPython prompt."""

    _project = None

    @property
    def project(self):
        """Project instance."""
        if self._project is None:
            import nodeps

            self._project = nodeps.Project()
        return self._project

    def in_prompt_tokens(self, cli=None):
        """In prompt tokens."""
        branch = latest = []
        if self.project.gh:
            branch = [
                (Token, " "),
                (Token.Generic, "↪"),
                (Token.Generic, self.project.gh.current()),
            ]
            latest = [
                (Token, " "),
                (Token.Name.Entity, self.project.gh.latest()),
            ]
        return [
            (Token, ""),
            (Token.OutPrompt, pathlib.Path().absolute().stem),
            *branch,
            *((Token, " "), (Token.Prompt, "©") if os.environ.get("VIRTUAL_ENV") else (Token, "")),
            (Token, " "),
            (Token.Name.Class, "v" + platform.python_version()),
            *latest,
            (Token, " "),
            (Token.Prompt, "["),
            (Token.PromptNum, str(self.shell.execution_count)),
            (Token.Prompt, "]: "),
            (
                Token.Prompt if self.shell.last_execution_succeeded else Token.Generic.Error,
                "❯ ",  # noqa: RUF001
            ),
        ]

    def out_prompt_tokens(self, cli=None):
        """Out Prompt."""
        return [
            (Token.OutPrompt, "Out<"),
            (Token.OutPromptNum, str(self.shell.execution_count)),
            (Token.OutPrompt, ">: "),
        ]


# </editor-fold>

# <editor-fold desc="Config">
if TYPE_CHECKING:
    try:
        from IPython.core.application import BaseIPythonApplication  # type: ignore[attr-defined]
        from IPython.core.completer import Completer, IPCompleter  # type: ignore[attr-defined]
        from IPython.core.formatters import BaseFormatter, PlainTextFormatter  # type: ignore[attr-defined]
        from IPython.core.history import HistoryAccessor, HistoryManager  # type: ignore[attr-defined]
        from IPython.core.interactiveshell import InteractiveShell  # type: ignore[attr-defined]
        from IPython.core.magic import MagicsManager  # type: ignore[attr-defined]
        from IPython.core.magics.logging import LoggingMagics  # type: ignore[attr-defined]
        from IPython.core.magics.script import ScriptMagics  # type: ignore[attr-defined]
        from IPython.core.profiledir import ProfileDir  # type: ignore[attr-defined]
        from IPython.core.shellapp import InteractiveShellApp  # type: ignore[attr-defined]
        from IPython.extensions.storemagic import StoreMagics  # type: ignore[attr-defined]
        from IPython.terminal.ipapp import TerminalIPythonApp  # type: ignore[attr-defined]
        from traitlets.config.application import Application  # type: ignore[attr-defined]


        class Config:
            Application: Application = None
            BaseFormatter: BaseFormatter = None
            BaseIPythonApplication: BaseIPythonApplication = None
            Completer: Completer = None
            HistoryAccessor: HistoryAccessor = None
            HistoryManager: HistoryManager = None
            InteractiveShell: InteractiveShell = None
            InteractiveShellApp: InteractiveShellApp = None
            IPCompleter: IPCompleter = None
            LoggingMagics: LoggingMagics = None
            MagicsManager: MagicsManager = None
            PlainTextFormatter: PlainTextFormatter = None
            ProfileDir: ProfileDir = None
            ScriptMagics: ScriptMagics = None
            StoreMagics: StoreMagics = None
            TerminalInteractiveShell: TerminalInteractiveShell = None
            TerminalIPythonApp: TerminalIPythonApp = None
            initialized: bool = False
    except ModuleNotFoundError:
        Config = None
else:
    Config = None

config: Config = get_config()

if "_pydev_bundle.pydev_ipython_console_011" in sys.modules:
    _pydev_bundle.pydev_ipython_console_011.PyDevTerminalInteractiveShell.automagic = True
    _pydev_bundle.pydev_ipython_console_011.PyDevTerminalInteractiveShell.banner1 = ""
    _pydev_bundle.pydev_ipython_console_011.PyDevTerminalInteractiveShell.banner2 = ""
    _pydev_bundle.pydev_ipython_console_011.PyDevTerminalInteractiveShell.colors = "Linux"
    _pydev_bundle.pydev_ipython_console_011.PyDevTerminalInteractiveShell.history_length = 30000
    _pydev_bundle.pydev_ipython_console_011.PyDevTerminalInteractiveShell.sphinxify_docstring = True

    _pydev_bundle.pydev_ipython_console_011.PyDevTerminalInteractiveShell.auto_match = True
    _pydev_bundle.pydev_ipython_console_011.PyDevTerminalInteractiveShell.autoformatter = "black"
    _pydev_bundle.pydev_ipython_console_011.PyDevTerminalInteractiveShell.highlighting_style = "monokai"
    if IPYTHON:
        _pydev_bundle.pydev_ipython_console_011.PyDevTerminalInteractiveShell.prompts = MyPrompt(IPYTHON)
    # Breaks PyCharm
    # _pydev_bundle.pydev_ipython_console_011.PyDevTerminalInteractiveShell.prompts_class = MyPrompt
    _pydev_bundle.pydev_ipython_console_011.PyDevTerminalInteractiveShell.simple_prompt = True
    _pydev_bundle.pydev_ipython_console_011.PyDevTerminalInteractiveShell.true_color = True
    _pydev_bundle.pydev_ipython_console_011.PyDevTerminalInteractiveShell.warn_venv = False

if config is not None and (not config or "initialized" not in config):
    config.initialized = True
    config.BaseIPythonApplication.ipython_dir = str(IPYTHONDIR)
    config.BaseIPythonApplication.verbose_crash = True
    config.Completer.auto_close_dict_keys = True
    config.InteractiveShellApp.exec_PYTHONSTARTUP = False
    config.InteractiveShellApp.extensions = IPYTHON_EXTENSIONS
    config.InteractiveShell.automagic = True
    config.InteractiveShell.banner1 = ""
    config.InteractiveShell.banner2 = ""
    config.InteractiveShell.colors = "Linux"
    config.InteractiveShell.history_length = 30000
    config.InteractiveShell.sphinxify_docstring = True
    config.IPCompleter.omit__names = 0
    config.MagicsManager.auto_magic = True
    config.PlainTextFormatter.max_seq_length = 0
    # AttributeError: 'PickleShareDB' object has no attribute 'keys'
    # If not db.keys() already then config.StoreMagics.autorestore will fail
    if hasattr(PickleShareDB(IPYTHON_PROFILE_DEFAULT_DIR / "db") if callable(PickleShareDB) else None, "keys"):
        config.StoreMagics.autorestore = True
    config.StoreMagics.autorestore = True
    config.TerminalInteractiveShell.auto_match = True
    config.TerminalInteractiveShell.autoformatter = "black"
    config.TerminalInteractiveShell.confirm_exit = False
    config.TerminalInteractiveShell.highlighting_style = "monokai"
    if IPYTHON:
        config.TerminalInteractiveShell.prompts = MyPrompt(IPYTHON)
    config.TerminalInteractiveShell.prompts_class = MyPrompt
    config.TerminalInteractiveShell.simple_prompt = False
    config.TerminalInteractiveShell.true_color = True
    config.TerminalInteractiveShell.warn_venv = False
    config.TerminalIPythonApp.display_banner = False
    config.Completer.auto_close_dict_keys = True
    config.IPCompleter.omit__names = 0
    config.MagicsManager.auto_magic = True
    config.PlainTextFormatter.max_seq_length = 0

if IPYTHON and config:
    IPYTHON.config |= config


# </editor-fold>

# <editor-fold desc="refresh_variables patch">
def _refresh_variables(ip: TerminalInteractiveShell):
    """Patch.

    AttributeError: 'PickleShareDB' object has no attribute 'keys'
    If not db.keys() already then config.StoreMagics.autorestore will fail
    """
    if hasattr(ip.db, "keys"):
        refresh_variables(ip)


if "IPython.extensions.storemagic" in sys.modules:
    IPython.extensions.storemagic.refresh_variables = _refresh_variables


# </editor-fold>

# <editor-fold desc="update_instances patch">
def _update_instances(old, new):
    """Path autoreload."""
    with contextlib.suppress(TypeError, AttributeError):
        update_instances(old, new)


if "IPython.extensions.autoreload" in sys.modules:
    IPython.extensions.autoreload.update_instances = _update_instances


# </editor-fold>

# <editor-fold desc="Python Startup">
def ipy():
    """Python Startup."""
    if not IPYTHON:
        try:
            import IPython

            os.environ["PYTHONSTARTUP"] = ""
            IPython.start_ipython(config=config)

            raise SystemExit
        except ModuleNotFoundError:
            pass


# </editor-fold>

def to_sys_path(path: pathlib.Path | str | None = None) -> list[str]:
    """Prepend path to sys.path if not in sys.path.

    Args:
        path: path to add, default None

    Returns:
        new sys.path
    """
    if path is not None and (_path := str(path)) not in sys.path:
        sys.path.insert(0, _path)

    return sys.path


for _i in (NODEPS_SRC, VIRTUAL_ENV_CWD_STARTUP, VIRTUAL_ENV_SRC):
    to_sys_path(_i)

if "IPython.core.shellapp" in sys.modules:
    # Only works with ipython
    IPython.core.shellapp.InteractiveShellApp.extensions = IPYTHON_EXTENSIONS

warnings.filterwarnings("ignore", ".*To exit:.*", UserWarning)
warnings.filterwarnings("ignore", ".*requires you to install the `pickleshare` library.*", UserWarning)
