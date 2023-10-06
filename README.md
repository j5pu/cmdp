# NoDeps

[![PyPI](https://img.shields.io/pypi/v/nodeps.svg)][pypi status]
[![Status](https://img.shields.io/pypi/status/nodeps.svg)][pypi status]
[![Python Version](https://img.shields.io/pypi/pyversions/nodeps)][pypi status]
[![License](https://img.shields.io/pypi/l/nodeps)][license]

[![Read the documentation at https://sbit.readthedocs.io/](https://img.shields.io/readthedocs/nodeps/latest.svg?label=Read%20the%20Docs)][read the docs]
[![Tests](https://github.com/j5pu/nodeps/workflows/Tests/badge.svg)][tests]
[![Codecov](https://codecov.io/gh/j5pu/nodeps/branch/main/graph/badge.svg)][codecov]

[pypi status]: https://pypi.org/project/nodeps/

[read the docs]: https://nodeps.readthedocs.io/

[tests]: https://github.com/j5pu/nodeps/actions?workflow=Tests

[codecov]: https://app.codecov.io/gh/j5pu/nodeps

[pre-commit]: https://github.com/pre-commit/pre-commit

[black]: https://github.com/psf/black

## Features

### Extras:
- `ansi`: for `getstdout` and `strip` function using `strip-ansi` library
- `echo`: for `echo` package using `click` library
- `log`: for `logger` function using `loguru` library
- `pickle`: for `cache` function using `jsonpickle` and `structlog` libraries
- `pth`: for `PTHBuildPy`, `PTHDevelop`, `PTHEasyInstall` and `PTHInstallLib` classes using `setuptools` library
- `pretty`: for `rich` library install and `icecream.ic` configuration 
- `repo`: for `Repo` class using `gitpython` library
- `requests`: for `python_latest`, `python_versions` and `request_x_api_key_json` functions that use the `requests` and `beautifulsoup4` libraries

Test imports uninstalling: `pip uninstall loguru beautifulsoup4 click jsonpickle strip_ansi structlog typer`
### PTH

Add to your `setup.cfg` and `<module>.pth` file in your package.

```ìni
[options]
cmdclass =
  build_py = nodeps.PTHBuildPy
  develop = nodeps.PTHDevelop
  easy_install = nodeps.PTHEasyInstall
  install_lib = nodeps.PTHInstallLib
```

Add to your `pyproject.toml`:

```toml
[build-system]
requires = [
    "nodeps",
    "setuptools_scm >= 8.0.3, <9",
    "wheel >= 0.41.2, <1"
]
```

## Installation

You can install _nodeps_ via [pip] from [PyPI]:

```console
$ pip install nodeps
```

You can install _nodeps_ with extras [pip] from [PyPI]:

```console
$ pip install nodeps[repo]
```

To install all extras (not including development extras):

```console
$ pip install nodeps[all]
```

## License

Distributed under the terms of the [MIT license][license],
_nodeps_ is free and open source software.

## Issues

If you encounter any problems,
please [file an issue] along with a detailed description.

## Credits

[@j5pu]: https://github.com/j5pu

[pypi]: https://pypi.org/

[file an issue]: https://github.com/j5pu/pproj/issues

[pip]: https://pip.pypa.io/

<!-- github-only -->

[license]: https://github.com/j5pu/pproj/blob/main/LICENSE
