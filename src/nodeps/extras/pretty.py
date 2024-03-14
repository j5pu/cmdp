"""NoDeps Pretty Module."""
__all__ = (
    "CONSOLE",
    "RICH_SUPPRESS",
    "ins",
    "is_idlelib",
    "is_repl",
    "is_terminal",
    "rich_install",
)

import sys
from io import BufferedRandom, BufferedReader, BufferedWriter, FileIO, TextIOWrapper
from typing import IO, Any, BinaryIO

try:
    # nodeps[pretty] extras
    import rich.console  # type: ignore[attr-defined]
    import rich.pretty  # type: ignore[attr-defined]
    import rich.traceback  # type: ignore[attr-defined]
    from rich.console import Console  # type: ignore[attr-defined]

    CONSOLE = rich.console.Console(color_system="standard")
    RICH_SUPPRESS = {"click", "_pytest", "pluggy", "rich", }
except ModuleNotFoundError:
    Console = object
    CONSOLE = None
    RICH_SUPPRESS = {}

OpenIO = BinaryIO | BufferedRandom | BufferedReader | BufferedWriter | FileIO | IO | TextIOWrapper


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


def rich_install():
    """Install rich."""
    if CONSOLE:
        rich.pretty.install(CONSOLE, expand_all=True)  # type: ignore[attr-defined]
        rich.traceback.install(show_locals=True, suppress=RICH_SUPPRESS)


rich_install()

if "rich.console" in sys.modules:
    # noinspection PyPropertyAccess,PyUnboundLocalVariable
    rich.console.Console.is_terminal = property(is_terminal)
