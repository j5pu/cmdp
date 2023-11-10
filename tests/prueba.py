from importlib import import_module

mod = import_module("nodeps")

print(dir(mod))
