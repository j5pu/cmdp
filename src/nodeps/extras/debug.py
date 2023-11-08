"""NoDeps Extras Pretty Module."""
__all__ = (
    "ic",
    "icc",
)

import os

# 768 y Cache 512

try:
    from icecream import IceCreamDebugger  # type: ignore[name-defined]

    ic = IceCreamDebugger(prefix="")
    icc = IceCreamDebugger(prefix="", includeContext=True)
    ic.enabled = icc.enabled = bool(os.environ.get("IC"))
except ModuleNotFoundError:
    def ic(*a):
        """Include Context."""
        return None if not a else a[0] if len(a) == 1 else a


    def icc(*a):
        """Include Context."""
        return None if not a else a[0] if len(a) == 1 else a
