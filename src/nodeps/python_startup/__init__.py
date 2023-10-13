"""PYTHONSTARTUP (Does not work with PyCharm."""
import os
import sys

os.environ['PYTHONSTARTUP'] = ''  # Prevent running this again

try:
    if not sys.argv[0]:
        import IPython

        from nodeps import load_ipython_extension
        if "IPYTHONDIR" in os.environ:
            del os.environ["IPYTHONDIR"]
        IPython.start_ipython(config=load_ipython_extension())
        raise SystemExit
except ModuleNotFoundError:
    pass
