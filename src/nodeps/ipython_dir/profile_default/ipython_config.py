"""IPython variables module."""  # noqa: INP001

import os

from nodeps.ipython_variables import (
    IPYTHONconfig,
    IPYTHON,
    IPYTHONDIR,
    IPYTHON_EXTENSIONS,
    IPYTHON_PROFILE_DEFAULT_DIR,
    MyPrompt,
)

try:
    # nodeps[ipython] extras
    from IPython.core.interactiveshell import PickleShareDB  # type: ignore[attr-defined]
except ModuleNotFoundError:
    PickleShareDB = None

config = IPYTHONconfig

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
    # if IPYTHON:
    #     config.TerminalInteractiveShell.prompts = MyPrompt(IPYTHON)
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


# <editor-fold desc="Python Startup">
def ipy():
    """Python Startup."""
    try:
        from IPython.core.getipython import get_ipython  # type: ignore[attr-defined]
    except ModuleNotFoundError:
        get_ipython = lambda *args: None  # noqa: E731

    if not get_ipython():
        try:
            import IPython

            os.environ["PYTHONSTARTUP"] = ""
            IPython.start_ipython(config=config)

            raise SystemExit
        except ModuleNotFoundError:
            pass

# </editor-fold>
