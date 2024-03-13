"""Python Startup Module."""  # noqa: INP001
import pathlib
import sys

if (_path := str(pathlib.Path(__file__).parent)) not in sys.path:
    sys.path.insert(0, _path)

from ipython_config import ipy

if not sys.argv:
    # python startup
    ipy()

if __name__ == "__main__":
    ipy()
