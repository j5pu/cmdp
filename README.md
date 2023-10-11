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

### Globals to set with nodeps commands
- IPython Profile :mod:`ipython_profile.profile_default.ipython_config`: `export IPYTHONDIR="$(ipythondir)"`
- Python Startup :mod:`python_startup.__init__`: `export PYTHONSTARTUP="$(pythonstartup)"`

### Automatic installation of packages

`PipMetaPathFinder` is a `sys.meta_path` finder that automatically installs packages when they are imported.

### Task dependencies
- `venv` runs `write` and `requirements`
- `build` runs  `venv`, `completions`, `docs` and `clean`.
- `tests` runs `build`, `ruff`, `pytest` and `tox`
- `publish` runs `tests`, `commit`, `tag`, `push`, `twine` and `clean`

### Completions

To install completions after a package is installed:
`p completions [name]` or `completions [name]`

### Repos

To synchronize (push or pull) all repos under `~/Archive` and `$HOME` run: `repos --sync` or `p repos --sync`

### pyproject.toml

#### Project

Project section information in `pyproject.toml` is automatically updated when `Project.write()` is called, is key is not in project. 
An empty `pyproject.toml` is needed.

#### Extras
To use all extras from nodeps to your project, add the following to your `pyproject.toml`:

```toml
[project.optional-dependencies]
dev = [
    "nodeps[dev]",
]
```

### docs conf.py and requirements.txt

doc `conf.py`,  `reference.md` and `requirements.txt` are automatically updated when `Project.write()` is called.

`usage.md` requires a click instance in `__main__.py`:
`<app_name>_click = typer.main.get_command(<Typer instance>)`

```md
# Usage

```{eval-rst}
.. click:: pdf.__main__:<app_name>_click
    :prog: reembolsos
    :nested: full
```

### Makefile

```makefile
brew:
	@p $@

browser:
	@$@

.PHONY: build
build:  # run: write, docs, clean and venv (requirements)
	@$@

builds:  # run: write, docs, clean and venv (requirements)
	@$@

clean:
	@$@

commit: tests
	@$@

completions:
	@$@

coverage:
	@p $@

.PHONY: docs
docs:
	@$@

latest:
	@$@

next:
	@$@

nodeps:
	@python3 -m pip install --upgrade -q $@[all,dev]

publish:  # runs: docs, tests (build (clean, venv (requirements)), pytest, ruff & tox), commit, tag, push, twine & clean
	@$@

pyenv:
	@pyenv install 3.11
	@pyenv install 3.12-dev

pytest:
	@p $@

pytests:
	@$@

requirement:
	@$@ --install

requirements:
	@$@

ruff:
	@p $@

secrets:
	@$@

test:
	@p $@

.PHONY: tests
tests:  # runs: build (clean, venv (requirements)), pytest, ruff and tox
	@$@

tox:
	@p $@

twine:
	@p $@

.PHONY: venv
venv:  # runs: requirements
	@$@

venvs:  # runs: requirements
	@$@

write:
	@p $@

.DEFAULT_GOAL := publish
```

### Extras:
- `ansi`: for `getstdout` and `strip` function using `strip-ansi` library
- `cli`: for `typer` to have CLI for `p` command
- `echo`: for `echo` package using `click` library
- `log`: for `logger` function using `loguru` library
- `pickle`: for `cache` function using `jsonpickle` and `structlog` libraries
- `pth`: for `PTHBuildPy`, `PTHDevelop`, `PTHEasyInstall` and `PTHInstallLib` classes using `setuptools` library
- `pretty`: for `rich` library install and `icecream.ic` configuration 
- `repo`: for `Repo` class using `gitpython` library
- `requests`: for `python_latest`, `python_versions` and `request_x_api_key_json` functions that use the `requests` and `beautifulsoup4` libraries

Test imports uninstalling: `pip uninstall loguru beautifulsoup4 click jsonpickle strip_ansi structlog typer`

### PTH

Add to your `setup.cfg` and `<mypackage>.pth` file in your package.

```ìni
[options]
cmdclass =
  build_py = nodeps.PTHBuildPy
  develop = nodeps.PTHDevelop
  easy_install = nodeps.PTHEasyInstall
  install_lib = nodeps.PTHInstallLib
[options.package_data]
mypackage =
  *.pth
```

Add to your `pyproject.toml`:

```toml
[build-system]
requires = [
    "nodeps",
    "setuptools >= 68.2.2, <69",
    "setuptools_scm >= 8.0.3, <9",
    "wheel >= 0.41.2, <1"
]
```

To verify that `nodeps.pth` is being installed use:
`python -c "import venv; print(venv.CORE_VENV_DEPS)"`

### Post install

File `_post_install.py` is automatically executed after `pip install` with the `pip` install patch.

## Installation

You can install _nodeps_ via [pip] from [PyPI]:

```console
$ pip install nodeps
```

You can install _nodeps_ with extras [pip] from [PyPI]:

```console
$ pip install nodeps[repo]
```

To install all extras but [dev] (not including development extras):

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

[file an issue]: https://github.com/j5pu/nodeps/issues

[pip]: https://pip.pypa.io/

<!-- github-only -->

[license]: https://github.com/j5pu/nodeps/blob/main/LICENSE

[command-line reference]: https://nodeps.readthedocs.io/en/latest/usage.html
