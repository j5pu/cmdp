"""IPython variables module.

Caveats:
    Imported at the beginning before iPython when other module
    Imported after IPython when in nodeps.

Workaround in PyCharm Console:
    ip = get_ipython()
    import nodeps.ipython_dir.profile_default.ipython_pycharm_startup
    file = nodeps.ipython_dir.profile_default.ipython_pycharm_startup.__file__
    ip.user_ns["__file__"] = file
    ip.user_ns["IPYTHON"] = ip
    ip.safe_execfile(file, ip.user_ns, raise_exceptions=True)
"""
__all__ = (
    "IPYTHONConfigType",
    "CWD_STARTUP",
    "CWD_SRC",
    "IPYTHONType",
    "NODEPS_MODULE_PATH",
    "NODEPS_NAME",
    "NODEPS_SRC",
    "VIRTUAL_ENV",
    "VIRTUAL_ENV_CWD_STARTUP",
    "VIRTUAL_ENV_SRC",
    "IPYTHONDIR",
    "IPYTHON_PROFILE_DEFAULT_DIR",
    "IPYTHON_CONFIG_FILE",
    "IPYTHON_EXTENSIONS_DIR",
    "IPYTHON_PYCHARM_STARTUP_FILE",
    "IPYTHON_EXTENSIONS_NODEPS",
    "IPYTHON_EXTENSIONS",
    "IPYTHON_STARTUP_DIR",
    "IPYTHON_STARTUP_IPY_FILES",
    "IPYTHON_STARTUP_PY_FILES",
    "PYTHONSTARTUP",
    "PYCHARM_CONSOLE",
    "RELOAD_EXTENSION",
    "IPYTHON",
    "IPYTHONconfig",
    "to_sys_path",
)

import contextlib
import os
import pathlib
import platform
import sys
import tomllib
import warnings
from typing import TypeAlias

try:
    # nodeps[ipython] extras
    import IPython.core.shellapp  # type: ignore[attr-defined]
    from IPython.core.application import BaseIPythonApplication  # type: ignore[attr-defined]
    from IPython.core.completer import Completer, IPCompleter  # type: ignore[attr-defined]
    from IPython.core.formatters import BaseFormatter, PlainTextFormatter  # type: ignore[attr-defined]
    from IPython.core.getipython import get_ipython  # type: ignore[attr-defined]
    from IPython.core.history import HistoryAccessor, HistoryManager  # type: ignore[attr-defined]
    from IPython.core.interactiveshell import InteractiveShell  # type: ignore[attr-defined]
    from IPython.core.magic import MagicsManager  # type: ignore[attr-defined]
    from IPython.core.magics.logging import LoggingMagics  # type: ignore[attr-defined]
    from IPython.core.magics.script import ScriptMagics  # type: ignore[attr-defined]
    from IPython.core.profiledir import ProfileDir  # type: ignore[attr-defined]
    from IPython.core.shellapp import InteractiveShellApp  # type: ignore[attr-defined]
    from IPython.extensions.autoreload import update_instances  # type: ignore[attr-defined]
    from IPython.extensions.storemagic import StoreMagics, refresh_variables  # type: ignore[attr-defined]
    from IPython.terminal.interactiveshell import TerminalInteractiveShell  # type: ignore[attr-defined]
    from IPython.terminal.ipapp import TerminalIPythonApp, load_default_config  # type: ignore[attr-defined]
    from IPython.terminal.prompts import Prompts, Token  # type: ignore[attr-defined]
    from traitlets.config.application import Application, get_config  # type: ignore[attr-defined]

except ModuleNotFoundError:
    IPython = None
    get_config = get_ipython = load_default_config = refresh_variables = update_instances = lambda *args: None
    Application = BaseFormatter = BaseIPythonApplication = Completer = HistoryAccessor = HistoryManager = \
        InteractiveShell = InteractiveShellApp = IPCompleter = LoggingMagics = MagicsManager = PlainTextFormatter = \
        ProfileDir = Prompts = ScriptMagics = StoreMagics = TerminalInteractiveShell = TerminalIPythonApp = Token = \
        object

try:
    import _pydev_bundle.pydev_ipython_console_011  # type: ignore[attr-defined]
    from _pydev_bundle.pydev_ipython_console_011 import (  # type: ignore[attr-defined]
        PyDebuggerTerminalInteractiveShell,  # type: ignore[attr-defined]
        PyDevTerminalInteractiveShell,  # type: ignore[attr-defined]
    )
except ModuleNotFoundError:
    _pydev_bundle = PyDebuggerTerminalInteractiveShell = PyDevTerminalInteractiveShell = object


# <editor-fold desc="IPython Config Type Class">
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


IPYTHONConfigType: TypeAlias = Config

# </editor-fold>


# <editor-fold desc="Variables">
CWD_STARTUP = pathlib.Path.cwd()
"""Startup CWD."""
CWD_SRC = _cwd_src if (_cwd_src := CWD_STARTUP / "src").is_dir() else None
"""CWD/src"""
IPYTHONType: TypeAlias = TerminalInteractiveShell | PyDebuggerTerminalInteractiveShell | PyDevTerminalInteractiveShell
NODEPS_MODULE_PATH = pathlib.Path(__file__).parent.parent
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

IPYTHONDIR = NODEPS_MODULE_PATH / "ipython_dir"
"""IPython Profile: `export IPYTHONDIR="$(ipythondir)"`."""

IPYTHON_PROFILE_DEFAULT_DIR = IPYTHONDIR / "profile_default"
IPYTHON_CONFIG_FILE = IPYTHON_PROFILE_DEFAULT_DIR / "ipython_config.py"
IPYTHON_EXTENSIONS_DIR = IPYTHONDIR / "extensions"
IPYTHON_PYCHARM_STARTUP_FILE = IPYTHON_PROFILE_DEFAULT_DIR / "ipython_pycharm_startup.py"
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

IPYTHON: IPYTHONType = get_ipython()
IPYTHONconfig: Config = get_config()


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

# <editor-fold desc="sys.path">
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


for _i in (IPYTHON_PROFILE_DEFAULT_DIR, NODEPS_SRC, VIRTUAL_ENV_CWD_STARTUP, VIRTUAL_ENV_SRC):
    to_sys_path(_i)


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
    # noinspection PyUnboundLocalVariable,PyUnresolvedReferences
    IPython.extensions.storemagic.refresh_variables = _refresh_variables


# </editor-fold>


# <editor-fold desc="update_instances patch">
def _update_instances(old, new):
    """Path autoreload."""
    with contextlib.suppress(TypeError, AttributeError):
        update_instances(old, new)


if "IPython.extensions.autoreload" in sys.modules:
    # noinspection PyUnboundLocalVariable,PyUnresolvedReferences
    IPython.extensions.autoreload.update_instances = _update_instances


# </editor-fold>


# <editor-fold desc="IPython PyCharm exec_lines patch">
def _pydev_ipython_frontend_init(self, is_jupyter_debugger=False):
    """_pydev_bundle.pydev_ipython_console_011._PyDevIPythonFrontEnd.__init__ patch."""
    # Create and initialize our IPython instance.
    self.is_jupyter_debugger = is_jupyter_debugger
    if is_jupyter_debugger:
        if hasattr(PyDebuggerTerminalInteractiveShell,
                   'new_instance') and PyDebuggerTerminalInteractiveShell.new_instance is not None:
            self.ipython = PyDebuggerTerminalInteractiveShell.new_instance
        else:
            # if we already have some InteractiveConsole instance (Python Console: Attach Debugger)
            # noinspection PyUnresolvedReferences
            if hasattr(PyDevTerminalInteractiveShell,
                       '_instance') and PyDevTerminalInteractiveShell._instance is not None:
                # noinspection PyUnresolvedReferences
                PyDevTerminalInteractiveShell.clear_instance()

            InteractiveShell.clear_instance()
            # noinspection PyUnresolvedReferences
            self.ipython = PyDebuggerTerminalInteractiveShell.instance(config=load_default_config())
            # noinspection PyUnresolvedReferences
            PyDebuggerTerminalInteractiveShell.new_instance = PyDebuggerTerminalInteractiveShell._instance
    elif hasattr(PyDevTerminalInteractiveShell, '_instance') and PyDevTerminalInteractiveShell._instance is not None:
        self.ipython = PyDevTerminalInteractiveShell._instance
    else:
        # noinspection PyUnresolvedReferences
        self.ipython = PyDevTerminalInteractiveShell.instance(config=load_default_config())

    self._curr_exec_line = 0
    self._curr_exec_lines = [
        "IPYTHON = get_ipython()",
        f"IPYTHON.safe_execfile('{IPYTHON_PYCHARM_STARTUP_FILE!s}', {{}}, raise_exceptions=True)",
    ]


if "_pydev_bundle.pydev_ipython_console_011" in sys.modules:
    # noinspection PyUnboundLocalVariable,PyUnresolvedReferences
    _pydev_bundle.pydev_ipython_console_011._PyDevIPythonFrontEnd.__init__ = _pydev_ipython_frontend_init

# </editor-fold>

# <editor-fold desc="PyCharm config patches">
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
# </editor-fold>

if "IPython.core.shellapp" in sys.modules:
    # Only works with ipython
    IPython.core.shellapp.InteractiveShellApp.extensions = IPYTHON_EXTENSIONS

warnings.filterwarnings("ignore", ".*To exit:.*", UserWarning)
warnings.filterwarnings("ignore", ".*requires you to install the `pickleshare` library.*", UserWarning)
