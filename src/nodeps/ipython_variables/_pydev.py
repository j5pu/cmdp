try:
    import _pydev_bundle.pydev_ipython_console_011  # type: ignore[attr-defined]
    from _pydev_bundle.pydev_ipython_console_011 import (  # type: ignore[attr-defined]
        PyDebuggerTerminalInteractiveShell,  # type: ignore[attr-defined]
        PyDevTerminalInteractiveShell,  # type: ignore[attr-defined]
        _PyDebuggerFrontEndContainer,  # type: ignore[attr-defined]
        _PyDevFrontEndContainer,  # type: ignore[attr-defined]
        _PyDevIPythonFrontEnd,  # type: ignore[attr-defined]
        create_editor_hook,  # type: ignore[attr-defined]
    )
except ModuleNotFoundError:
    _pydev_bundle = _PyDevIPythonFrontEnd = PyDebuggerTerminalInteractiveShell = PyDevTerminalInteractiveShell = object

# <editor-fold desc="IPython PyCharm exec_lines patch">


class PyDevTerminal(PyDevTerminalInteractiveShell):
    def __init__(self, *args, **kwargs):
        print(self.__init__)
        super().__init__(*args, **kwargs)


class PyDebuggerTerminal(PyDebuggerTerminalInteractiveShell):
    def __init__(self, *args, **kwargs):
        print(self.__init__)

        super().__init__(*args, **kwargs)


class PyDevIPythonFrontEnd(_PyDevIPythonFrontEnd):
    def __init__(self, is_jupyter_debugger=False):
        print(self.__init__)

        super().__init__(is_jupyter_debugger=is_jupyter_debugger)


def _get_pydev_ipython_frontend(rpc_client, is_jupyter_debugger=False):
    """_pydev_bundle.pydev_ipython_console_011._get_pydev_ipython_frontend patch."""
    if is_jupyter_debugger:
        if _PyDebuggerFrontEndContainer._instance is None:
            _PyDebuggerFrontEndContainer._instance = PyDevIPythonFrontEnd(is_jupyter_debugger)

        return _PyDebuggerFrontEndContainer._instance

    if _PyDevFrontEndContainer._instance is None:
        _PyDevFrontEndContainer._instance = PyDevIPythonFrontEnd(is_jupyter_debugger)

    if _PyDevFrontEndContainer._last_rpc_client != rpc_client:
        _PyDevFrontEndContainer._last_rpc_client = rpc_client

        # Back channel to PyDev to open editors (in the future other
        # info may go back this way. This is the same channel that is
        # used to get stdin, see StdIn in pydev_console_utils)
        _PyDevFrontEndContainer._instance.ipython.hooks['editor'] = create_editor_hook(rpc_client)

        # Note: setting the callback directly because setting it with set_hook would actually create a chain instead
        # of overwriting at each new call).
        # _PyDevFrontEndContainer._instance.ipython.set_hook('editor',
        # create_editor_hook(pydev_host, pydev_client_port))

    return _PyDevFrontEndContainer._instance


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
    if InteractiveShellABC:
        InteractiveShellABC.register(PyDevTerminal)  # @UndefinedVariable
        InteractiveShellABC.register(PyDebuggerTerminal)
    _pydev_bundle.get_pydev_ipython_frontend = _get_pydev_ipython_frontend
    _pydev_bundle.pydev_ipython_console_011._PyDevIPythonFrontEnd.__init__ = _pydev_ipython_frontend_init

# </editor-fold>
