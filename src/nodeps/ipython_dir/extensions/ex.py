"""Rich install module."""  # noqa: INP001

from nodeps.ipython_dir.profile_default.ipython_config import NODEPS_NAME, IPYTHONType


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
    i.ex("import asyncio.base_events; asyncio.base_events.BaseEventLoop.slow_callback_duration = 1.5")
    i.ex(f"from {NODEPS_NAME} import rich_install; rich_install()")
