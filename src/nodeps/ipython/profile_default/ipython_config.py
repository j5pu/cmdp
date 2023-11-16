"""IPython Module."""
from __future__ import annotations

__all__ = (
    "IPYTHONDIR",
    "NODEPS_EXTENSION",
    "NODEPS_EXTENSIONS",
    "PYTHONSTARTUP",
    "ins",
    "ipy",
    "is_idlelib",
    "is_repl",
    "is_terminal",
    "load_ipython_extension",
)

import contextlib
import os
import pathlib
import platform
import sys
import warnings
from pathlib import Path
from typing import TYPE_CHECKING, Any

try:
    import IPython.core.shellapp  # type: ignore[attr-defined]
    from IPython.core.getipython import get_ipython  # type: ignore[attr-defined]
    from IPython.core.magic import Magics, line_magic, magics_class  # type: ignore[attr-defined]
    from IPython.terminal.prompts import Prompts, Token  # type: ignore[attr-defined]
    from traitlets.config.application import get_config  # type: ignore[attr-defined]
except ModuleNotFoundError as e:
    print(e)
    get_config = get_ipython = line_magic = magics_class = lambda *args: None
    Magics = Prompts = Token = object

try:
    from pickleshare import PickleShareDB  # type: ignore[attr-defined]
except ModuleNotFoundError:
    PickleShareDB = None

try:
    # nodeps[pretty] extras
    import rich.console  # type: ignore[attr-defined]
    import rich.pretty  # type: ignore[attr-defined]
    import rich.traceback  # type: ignore[attr-defined]

    CONSOLE = rich.console.Console(color_system="standard")
    RICH_SUPPRESS = {"click", "_pytest", "pluggy", "rich", }
    rich.pretty.install(CONSOLE, expand_all=True)  # type: ignore[attr-defined]
    rich.traceback.install(show_locals=True, suppress=RICH_SUPPRESS)  # type: ignore[attr-defined]
except ModuleNotFoundError:
    CONSOLE = None

if TYPE_CHECKING:
    from io import BufferedRandom, BufferedReader, BufferedWriter, FileIO, TextIOWrapper
    from typing import IO, BinaryIO

    OpenIO = BinaryIO | BufferedRandom | BufferedReader | BufferedWriter | FileIO | IO | TextIOWrapper

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
        from IPython.terminal.interactiveshell import TerminalInteractiveShell  # type: ignore[attr-defined]
        from IPython.terminal.ipapp import TerminalIPythonApp  # type: ignore[attr-defined]
        from IPython.terminal.prompts import Prompts, Token  # type: ignore[attr-defined]
        from rich.console import Console  # type: ignore[name-defined]
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
    except ModuleNotFoundError:
        Config = Console = Prompts = Token = object

_cwd = Path.cwd()
_dir = Path(__file__).parent

IPYTHONDIR = str(_dir.parent)
"""IPython Profile: `export IPYTHONDIR="$(ipythondir)"`."""
NODEPS_EXTENSION = Path(__file__).stem
NODEPS_EXTENSIONS = ["IPython.extensions.autoreload", NODEPS_EXTENSION, "IPython.extensions.storemagic", "rich"]
PYTHONSTARTUP = str(_dir / "python_startup.py")
"""Python Startup :mod:`python_startup.__init__`: `export PYTHONSTARTUP="$(pythonstartup)"`."""
NODEPS_SRC = str(_dir.parent.parent.parent)
"""Nodeps src directory."""


if str(_dir) not in sys.path:
    sys.path.insert(0, str(_dir))

if str(_cwd) not in sys.path:
    sys.path.insert(0, str(_cwd))

if (_src := _cwd / "src").is_dir() and str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

if NODEPS_SRC not in sys.path:
    sys.path.insert(0, NODEPS_SRC)


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


@magics_class
class ReloadMagic(Magics):
    """Nodeps magic class."""

    @line_magic
    def reload(self, _=""):
        """Nodeps magic."""
        self.shell.run_line_magic("reload_ext", NODEPS_EXTENSION)
        self.shell.run_line_magic("autoreload", "3")
        # self.shell.run_cell(f"print('reload run_cell: {NODEPS_EXTENSION}')")


def ins(obj: Any, *, _console: Console | None = None, title: str | None = None, _help: bool = False,
        methods: bool = True, docs: bool = False, private: bool = True,
        dunder: bool = False, sort: bool = True, _all: bool = False, value: bool = True, ):
    """Wrapper :func:`rich.inspect` for :class:`rich._inspect.Inspect`.

    Changing defaults to: ``docs=False, methods=True, private=True``.

    Inspect any Python object.

    Examples:
        >>> from nodeps import ins
        >>>
        >>> # to see summarized info.
        >>> ins(ins)  # doctest: +SKIP
        >>> # to not see methods.
        >>> ins(ins, methods=False)  # doctest: +SKIP
        >>> # to see full (non-abbreviated) help.
        >>> ins(ins, help=True)  # doctest: +SKIP
        >>> # to not see private attributes (single underscore).
        >>> ins(ins, private=False)  # doctest: +SKIP
        >>> # to see attributes beginning with double underscore.
        >>> ins(ins, dunder=True)  # doctest: +SKIP
        >>> # to see all attributes.
        >>> ins(ins, _all=True)  # doctest: +SKIP
        '

    Args:
        obj (Any): An object to inspect.
        _console (Console, optional): Rich Console.
        title (str, optional): Title to display over inspect result, or None use type. Defaults to None.
        _help (bool, optional): Show full help text rather than just first paragraph. Defaults to False.
        methods (bool, optional): Enable inspection of callables. Defaults to False.
        docs (bool, optional): Also render doc strings. Defaults to True.
        private (bool, optional): Show private attributes (beginning with underscore). Defaults to False.
        dunder (bool, optional): Show attributes starting with double underscore. Defaults to False.
        sort (bool, optional): Sort attributes alphabetically. Defaults to True.
        _all (bool, optional): Show all attributes. Defaults to False.
        value (bool, optional): Pretty print value. Defaults to True.
    """
    rich.inspect(obj=obj, console=_console or CONSOLE, title=title, help=_help, methods=methods, docs=docs,
                 private=private, dunder=dunder, sort=sort, all=_all, value=value)


def ipy():
    """Starts IPython."""
    try:
        import IPython

        os.environ["PYTHONSTARTUP"] = ""
        IPython.start_ipython(config=config)
        raise SystemExit
    except ModuleNotFoundError:
        pass


def is_idlelib() -> bool:
    """Is idle repl."""
    return hasattr(sys.stdin, "__module__") and sys.stdin.__module__.startswith("idlelib")


def is_repl() -> bool:
    """Check if it is a repl."""
    return any([hasattr(sys, "ps1"), "pythonconsole" in sys.stdout.__class__.__module__, is_idlelib()])


def is_terminal(self: Console | OpenIO | None = None) -> bool:
    """Patch for rich console is terminal.

    Examples:
        >>> import time
        >>> from rich.console import Console
        >>> from rich.json import JSON
        >>> from rich import print_json
        >>>
        >>> c = Console()
        >>> with c.status("Working...", spinner="material"):  # doctest: +SKIP
        ...    time.sleep(2)
        >>>
        >>> c.log(JSON('["foo", "bar"]'))  # doctest: +SKIP
        >>>
        >>> print_json('["foo", "bar"]')  # doctest: +SKIP
        >>>
        >>> c.log("Hello, World!")  # doctest: +SKIP
        >>> c.print([1, 2, 3])  # doctest: +SKIP
        >>> c.print("[blue underline]Looks like a link")  # doctest: +SKIP
        >>> c.print(locals())  # doctest: +SKIP
        >>> c.print("FOO", style="white on blue")  # doctest: +SKIP
        >>>
        >>> blue_console = Console(style="white on blue")  # doctest: +SKIP
        >>> blue_console.print("I'm blue. Da ba dee da ba di.")  # doctest: +SKIP
        >>>
        >>> c.input("What is [i]your[/i] [bold red]name[/]? :smiley: ")  # doctest: +SKIP

    References:
        Test with: `print("[italic red]Hello[/italic red] World!", locals())`

        `Rich Inspect <https://rich.readthedocs.io/en/stable/traceback.html?highlight=sitecustomize>`_

        ``rich.traceback.install(suppress=[click])``

        To see the spinners: `python -m rich.spinner`
        To print json from the comamand line: `python -m rich.json cats.json`

        `Rich Console <https://rich.readthedocs.io/en/stable/console.html>`_

        Input: `console.input("What is [i]your[/i] [bold red]name[/]? :smiley: ")`
    """
    if hasattr(self, "_force_terminal") and self._force_terminal is not None:
        return self._force_terminal

    if is_idlelib():
        return False

    if hasattr(self, "is_jupyter") and self.is_jupyter:
        return False

    if hasattr(self, "_force_terminal") and self._environ.get("FORCE_COLOR"):
        self._force_terminal = True
        return True

    try:
        return any(
            [
                is_repl(),
                hasattr(self, "isatty") and self.isatty(),
                hasattr(self, "file") and hasattr(self.file, "isatty") and self.file.isatty(),
            ]
        )
    except ValueError:
        return False


def load_ipython_extension(i: TerminalInteractiveShell | None = None):
    """IPython extension.

    We are entering twice at startup: from $PYTHONSTARTUP and ipython is None
        and from $IPYTHONDIR to load nodeps extension.

    The `ipython` argument is the currently active `InteractiveShell`
    instance, which can be used in any way. This allows you to register
    new magics or aliases, for example.

    https://ipython.readthedocs.io/en/stable/config/extensions/index.html


    self.shell.run_code("from %s import Test" % mod_name)
    self.shell.run_code("test = Test()")
    self.shell.magic_autoreload("2")
    self._reloader.
    self.auto_magics.autoreload(parameter)

    i.extension_manager.shell
    i.extension_manager.shell.run_code()
    i.extension_manager.shell.run_line_magic("autoreload", "3")
    i.user_ns

    Before extension is loaded:
        - almost no globals
        - and only nodeps in sys.modules
    """
    # load_ipython_extension() called in <module >
    load = __file__ == sys._getframe(1).f_code.co_filename
    i = i or ipython

    if i:
        i.register_magics(ReloadMagic)
        loaded = i.extension_manager.loaded
        if NODEPS_EXTENSION not in loaded:
            for extension in NODEPS_EXTENSIONS:
                if (extension not in loaded and
                        (extension != NODEPS_EXTENSION or (extension == NODEPS_EXTENSION and load))):
                    i.extension_manager.load_extension(extension)
        i.prompts = MyPrompt(i)
        i.user_ns["test_rich"] = [True, 1, "a"]
        # i.run_line_magic("store", "test_rich")
        i.run_line_magic("autoreload", "3")
        # i.run_cell("print('ipython run_cell: hello!')")
        # HACER: does not import in pycharm __all__, however user_ns gets updated and modules
        if env := os.environ.get("VIRTUAL_ENV"):
            module = Path(env).parent.name
            # i.run_cell(f"from {module} import *")
            i.ex(f"from {module} import *")
        elif _src.is_dir():
            top = _src.parent
            if (top / "pyproject.toml").is_file():
                i.ex(f"from {top.name} import *")

    rich.pretty.install(CONSOLE, expand_all=True)  # type: ignore[attr-defined]
    rich.traceback.install(show_locals=True, suppress=RICH_SUPPRESS)  # type: ignore[attr-defined]
    import asyncio.base_events

    asyncio.base_events.BaseEventLoop.slow_callback_duration = 1.5
    warnings.filterwarnings("ignore", ".*To exit:.*", UserWarning)


config: Config = get_config()
ipython: TerminalInteractiveShell = get_ipython()

if config is not None:
    # AttributeError: 'PickleShareDB' object has no attribute 'keys'
    # If not db.keys() already then config.StoreMagics.autorestore will fail
    db = PickleShareDB(Path(IPYTHONDIR) / "profile_default/db") if PickleShareDB else None
    config.BaseIPythonApplication.ipython_dir = IPYTHONDIR
    config.BaseIPythonApplication.verbose_crash = True
    config.Completer.auto_close_dict_keys = True
    config.InteractiveShell.automagic = True
    config.InteractiveShell.banner1 = ""
    config.InteractiveShell.banner2 = ""
    config.InteractiveShell.colors = "Linux"
    config.InteractiveShell.history_length = 30000
    config.InteractiveShell.sphinxify_docstring = True
    config.TerminalIPythonApp.exec_lines = [
        "%autoreload 3",
        # "print('exec_lines: hello!')",
    ]
    config.InteractiveShellApp.extensions = NODEPS_EXTENSIONS
    config.InteractiveShellApp.exec_PYTHONSTARTUP = False
    config.IPCompleter.omit__names = 0
    config.MagicsManager.auto_magic = True
    config.PlainTextFormatter.max_seq_length = 0
    if hasattr(db, "keys"):
        config.StoreMagics.autorestore = True
    config.TerminalInteractiveShell.auto_match = True
    config.TerminalInteractiveShell.autoformatter = "black"
    config.TerminalInteractiveShell.confirm_exit = False
    config.TerminalInteractiveShell.highlighting_style = "monokai"
    config.TerminalInteractiveShell.prompts_class = MyPrompt
    config.TerminalInteractiveShell.simple_prompt = False
    config.TerminalInteractiveShell.true_color = True
    config.TerminalIPythonApp.display_banner = False
    config.Completer.auto_close_dict_keys = True
    config.IPCompleter.omit__names = 0
    config.MagicsManager.auto_magic = True
    config.PlainTextFormatter.max_seq_length = 0
    if ipython:
        ipython.config = config

    if "IPython.core.shellapp" in sys.modules:
        # noinspection PyUnboundLocalVariable
        IPython.core.shellapp.InteractiveShellApp.extensions = NODEPS_EXTENSIONS

with contextlib.suppress(ValueError):
    if "do_import" in sys._getframe(8).f_code.co_name:
        load_ipython_extension()

if "rich.console" in sys.modules:
    # noinspection PyPropertyAccess,PyUnboundLocalVariable
    rich.console.Console.is_terminal = property(is_terminal)
