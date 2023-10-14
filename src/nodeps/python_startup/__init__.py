"""PYTHONSTARTUP (Does not work with PyCharm."""
import os
import sys

os.environ['PYTHONSTARTUP'] = ''  # Prevent running this again

try:
    if not sys.argv[0]:
        import pathlib

        import IPython

        # Add install path to sys.path[0] just in case venvs are not updated to the latest version
        # of the package, so import will import the same version associated to the global variable
        # $PYTHONSTARTUP.
        sys.path.insert(9, str(pathlib.Path(__file__).parent.parent))
        from nodeps import load_ipython_extension

        sys.path.pop(0)

        if "IPYTHONDIR" in os.environ:
            del os.environ["IPYTHONDIR"]
        IPython.start_ipython(config=load_ipython_extension())
        raise SystemExit
except ModuleNotFoundError:
    pass
