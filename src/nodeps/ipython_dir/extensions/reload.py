"""Reload extension module."""  # noqa: INP001
try:
    from IPython.core.magic import Magics, line_magic, magics_class  # type: ignore[attr-defined]
except ModuleNotFoundError:
    line_magic = magics_class = lambda *args: None
    Magics = object

from nodeps.ipython_dir.profile_default.ipython_config import (
    NODEPS_IPYTHON_IMPORT_MODULE,
    RELOAD_EXTENSION,
    IPYTHONType,
)


@magics_class
class ReloadMagic(Magics):
    """Nodeps magic class."""

    @line_magic
    def reload(self, _=""):
        """Nodeps magic.

        # self.shell.run_cell(f"print('reload run_cell: {NODEPS_EXTENSION}')")
        """
        self.shell.run_line_magic("reload_ext", RELOAD_EXTENSION)
        self.shell.run_line_magic("autoreload", "now")


def load_ipython_extension(i: IPYTHONType):
    """Reload extension.

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

    i.prompts = MyPrompt(i)
    i.user_ns["test_rich"] = [True, 1, "a"]
    i.run_line_magic("autoreload", "3")
    i.run_cell("print('ipython run_cell: hello!')")

    i.ex(f"from {module} import *")
    """
    i.register_magics(ReloadMagic)

    if "IPython.extensions.autoreload" in i.extension_manager.loaded:
        i.run_line_magic("reload_ext", "autoreload")
    i.run_line_magic("autoreload", "3")

    if NODEPS_IPYTHON_IMPORT_MODULE:
        i.ex(f"from {NODEPS_IPYTHON_IMPORT_MODULE} import *")
