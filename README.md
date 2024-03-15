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

### pytest fixtures

```python
import pytest
from typer.testing import Result
from nodeps.fixtures import skip_docker, Repos, Cli

@skip_docker
def test_skip_docker(local: bool):
    """Fixture to see if or --local passed to pytest or DOCKER or CI.

    Examples:
        pytest --local
        pytest --local tests/test_fixture.py::test_fixture_local
        pytest tests/test_fixture.py  # docker -> 2 skipped
        pytest tests/test_fixture.py  # 0 skipped
    """
    assert local is False

@pytest.mark.skipif("config.getoption('local') is True", reason='--local option provided')
def test_func_skipif_local_docker(local: bool):
    """Should run if local is False or not --local in command."""
    assert local is False


def test_fixture_repos(repos: Repos):
    """Test that repos are created and pushed."""
    assert (repos.local.top / "README.md").is_file()
    assert repos.local.git.cat_file("-e", "origin/main:README.md") == ""
    assert (repos.clone.top / "README.md").is_file()

@pytest.mark.parametrize("cli", [["command", "--option"]], indirect=True)
def test_current(cli: Cli):
   assert cli.result.exit_code == 0
   assert cli.result.stdout == "main"


@pytest.mark.parametrize("clirun", [["command", "--option"]], indirect=True)
def test_current(clirun: Result):
   assert clirun.exit_code == 0
   assert clirun.stdout == "main"
```

```bash
pytest --local tests/test_docker.py  # in macos to skip
pytest tests/test_docker.py # in docker to skip
```

### IPython extension

Add the following to PyCharm Console:

```python
# noinspection PyUnresolvedReferences
import nodeps
```

```ìpython
In [1]: %load_ext reload
In [2]: %reload_ext reload
In [3]: reload  # magic command
```

It is the same as:

```python
import IPython
IPython.start_ipython(["--ext=nodeps"])
```

### Env class and LOG

#### Searches for `.env` in cwd and up using `envsh` function

Usage: `env = Env()`.

- `LOGURU_LEVEL` will be set in `os.environ`.
- `LOG_LEVEL` will be set and parsed to int for `logging` module. `logger.setLevel(env.LOG_LEVEL)`

Posible values for `LOGURU_LEVEL` and `LOG_LEVEL`: "TRACE", "DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL".
`LOG_LEVEL` also accepts lower case or int.

#### Searches for `settings.ini` in cwd and up. If file is found `python-decouple` is used.

Usage:

- `var = Env()._config("VAR", default=False, cast=bool)`
- `extensions = {*Env()._config('EXTENSIONS', default=str(extensions), cast=decouple.Csv(post_process=set)), *extensions}`

To change decouple to use both `settings.ini` and `.env`:

```python
import collections
import decouple  # type: ignore[attr-defined]
from nodeps import Path

EXTENSIONS = ["foo", "boo"]
cwd = Path.cwd()
files = (
    decouple.RepositoryIni(path.absolute()) if path.suffix == ".ini" else decouple.RepositoryEnv(".env")
    for file in ("settings.ini", )  # ".env" process by envbash()
    if (path := cwd.find_up())
)
config = decouple.Config(collections.ChainMap(*files))
EXTENSIONS = {
    *config(
        "EXTENSIONS", default=",".join(EXTENSIONS), cast=decouple.Csv(post_process=set)
    ),
    *EXTENSIONS,
}
```

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
- `cli`: for `typer` to have CLI for `p` command (autoinstall with `pipmetapathfinder`)
- `echo`: for `echo` package using `click` library
- `env`: for `Env` class using `python-decouple` library
- `log`: for `logger` function using `loguru` library
- `pickle`: for `cache` function using `jsonpickle` and `structlog` libraries
- `pth`: for `PTHBuildPy`, `PTHDevelop`, `PTHEasyInstall` and `PTHInstallLib` classes using `setuptools` library
- `pretty`: for `rich` library install and `icecream.ic` configuration
- `repo`: for `Repo` class using `gitpython` library
- `requests`: for `python_latest`, `python_versions` and `request_x_api_key_json` functions that use the `requests` and `beautifulsoup4` libraries

`tomlkit` package is autoinstall with `pipmetapathfinder` for `pyproject.toml` file manipulation in `Project` class and `__main__.py`.

*Aggregated extras*:

- nodeps[all] includes all extras except dev.
- nodeps[dev] includes all dev extras.
- nodeps[full] includes all extras including dev [all,dev].

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

## [tests in docker](.cliactions.yaml)

```shell
./docker/docker.sh 3.11-slim-bash
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
