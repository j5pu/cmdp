"""Python Startup Module."""
import sys
from pathlib import Path

try:
    sys.path.insert(0, str(Path(__file__).parent))
    from ipython_config import ipy
finally:
    sys.path.pop(0)

if not sys.argv:
    # python startup
    ipy()


if __name__ == "__main__":
    ipy()
