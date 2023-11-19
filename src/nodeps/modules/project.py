"""Project Module."""
from __future__ import annotations

__all__ = ("Project",)

import copy
import dataclasses
import datetime
import importlib.metadata
import importlib.util
import pathlib
import shutil
import subprocess
import sys
import sysconfig
import types
from contextvars import ContextVar
from typing import ClassVar

from nodeps.modules.classes import ColorLogger, ConfigParser
from nodeps.modules.constants import (
    AUTHOR,
    CI,
    DOCKER,
    DOCKER_COMMAND,
    EMAIL,
    GIT,
    NODEPS_PROJECT_NAME,
    NODEPS_TOP,
    PYTHON_DEFAULT_VERSION,
    PYTHON_VERSIONS,
)
from nodeps.modules.enums import Bump, ProjectRepos
from nodeps.modules.errors import CalledProcessError, InvalidArgumentError
from nodeps.modules.functions import completions, dict_sort, findup, in_tox, suppress, urljson, which
from nodeps.modules.gh import Gh
from nodeps.modules.metapath import pipmetapathfinder
from nodeps.modules.path import FileConfig, Path, toiter

NODEPS_QUIET: ContextVar[bool] = ContextVar("NODEPS_QUIET", default=True)
"""Global variable to supress warn in setuptools"""


@dataclasses.dataclass
class Project:
    """Project Class."""

    data: Path | str | types.ModuleType = None
    """File, directory or name (str or path with one word) of project (default: current working directory)"""
    brewfile: Path | None = dataclasses.field(default=None, init=False)
    """Data directory Brewfile"""
    ci: bool = dataclasses.field(default=False, init=False)
    """running in CI or tox"""
    data_dir: Path | None = dataclasses.field(default=None, init=False)
    """Data directory"""
    directory: Path | None = dataclasses.field(default=None, init=False)
    """Parent of data if data is a file or None if it is a name (one word)"""
    docsdir: Path | None = dataclasses.field(default=None, init=False)
    """Docs directory"""
    gh: Gh = dataclasses.field(default=None, init=False)
    git: str = dataclasses.field(default="git", init=False)
    """git -C directory if self.directory is not None"""
    installed: bool = dataclasses.field(default=False, init=False)
    name: str = dataclasses.field(default=None, init=False)
    """Pypi project name from setup.cfg, pyproject.toml or top name or self.data when is one word"""
    profile: Path | None = dataclasses.field(default=None, init=False)
    """Data directory profile.d"""
    pyproject_toml: FileConfig = dataclasses.field(default_factory=FileConfig, init=False)
    repo: Path = dataclasses.field(default=None, init=False)
    """top or superproject"""
    root: Path = dataclasses.field(default=None, init=False)
    """pyproject.toml or setup.cfg parent or superproject or top directory"""
    source: Path | None = dataclasses.field(default=None, init=False)
    """sources directory, parent of __init__.py or module path"""
    clean_match: ClassVar[list[str]] = ["*.egg-info", "build", "dist"]
    rm: dataclasses.InitVar[bool] = False
    """remove cache"""

    def __post_init__(self, rm: bool = False):  # noqa: PLR0912, PLR0915
        """Post init."""
        self.ci = any([in_tox(), CI, DOCKER])
        self.data = self.data if self.data else Path.cwd()
        data = Path(self.data.__file__ if isinstance(self.data, types.ModuleType) else self.data)
        if (
                (isinstance(self.data, str) and len(toiter(self.data, split="/")) == 1)
                or (isinstance(self.data, pathlib.PosixPath) and len(self.data.parts) == 1)
        ) and (str(self.data) != "/"):
            if r := self.repos(ret=ProjectRepos.DICT, rm=rm).get(
                self.data if isinstance(self.data, str) else self.data.name
            ):
                self.directory = r
        elif data.is_dir():
            self.directory = data.absolute()
        elif data.is_file():
            self.directory = data.parent.absolute()
        else:
            msg = f"Invalid argument: {self.data=}"
            raise InvalidArgumentError(msg)

        if self.directory:
            self.git = f"git -C '{self.directory}'"
            if (path := findup(self.directory, name="pyproject.toml", uppermost=True)) and (
                    path.parent / ".git"
            ).exists():
                path = path[0] if isinstance(path, list) else path
                with pipmetapathfinder():
                    import tomlkit
                with Path.open(path, "rb") as f:
                    self.pyproject_toml = FileConfig(path, tomlkit.load(f))
                self.name = self.pyproject_toml.config.get("project", {}).get("name")
                self.root = path.parent
            elif (path := findup(self.directory, name=".git", kind="exists", uppermost=True)) and (
                    path.parent / ".git"
            ).exists():
                self.root = path.parent
                self.name = self.root.name

            if self.root:
                self.gh = Gh(self.root)
                self.repo = self.gh.top() or self.gh.superproject()
            purelib = sysconfig.get_paths()["purelib"]
            if root := self.root or self.repo:
                self.root = root.absolute()
                if (src := (root / "src")) and (str(src) not in sys.path):
                    sys.path.insert(0, str(src))
            elif self.directory.is_relative_to(purelib):
                self.name = Path(self.directory).relative_to(purelib).parts[0]
            self.name = self.name if self.name else self.root.name if self.root else None
        else:
            self.name = str(self.data)

        try:
            if self.name and ((spec := importlib.util.find_spec(self.name)) and spec.origin):
                self.source = Path(spec.origin).parent if "__init__.py" in spec.origin else Path(spec.origin)
                self.installed = True
                self.root = self.root if self.root else self.source.parent
                purelib = sysconfig.get_paths()["purelib"]
                self.installed = bool(self.source.is_relative_to(purelib) or Path(purelib).name in str(self.source))
        except (ModuleNotFoundError, ImportError):
            pass

        if self.source:
            self.data_dir = d if (d := self.source / "data").is_dir() else None
            if self.data_dir:
                self.brewfile = b if (b := self.data_dir / "Brewfile").is_file() else None
                self.profile = pr if (pr := self.data_dir / "profile.d").is_dir() else None
        if self.root:
            self.docsdir = doc if (doc := self.root / "docs").is_dir() else None
            if self.gh is None and (self.root / ".git").exists():
                self.gh = Gh(self.root)
        self.log = ColorLogger.logger(__name__)

    def info(self, msg: str):
        """Logger info."""
        self.log.info(msg, extra={"extra": self.name})

    def warning(self, msg: str):
        """Logger warning."""
        self.log.warning(msg, extra={"extra": self.name})

    def bin(self, executable: str | None = None, version: str = PYTHON_DEFAULT_VERSION) -> Path:  # noqa: A003
        """Bin directory.

        Args;
            executable: command to add to path
            version: python version
        """
        return Path(self.executable(version=version)).parent / executable if executable else ""

    def brew(self, c: str | None = None) -> int:
        """Runs brew bundle."""
        if which("brew") and self.brewfile and (c is None or not which(c)):
            rv = subprocess.run(
                [
                    "brew",
                    "bundle",
                    "--no-lock",
                    "--quiet",
                    f"--file={self.brewfile}",
                ],
                shell=False,
            ).returncode
            self.info(self.brew.__name__)
            return rv
        return 0

    def browser(self, version: str = PYTHON_DEFAULT_VERSION, quiet: bool = True) -> int:
        """Build and serve the documentation with live reloading on file changes.

        Arguments:
            version: python version
            quiet: quiet mode (default: True)
        """
        ContextVar("NODEPS_QUIET").set(quiet)

        if not self.docsdir:
            return 0
        build_dir = self.docsdir / "_build"
        q = "-Q" if quiet else ""
        if build_dir.exists():
            shutil.rmtree(build_dir)

        if (
                subprocess.check_call(
                    f"{self.executable(version=version)} -m sphinx_autobuild {q} {self.docsdir} {build_dir}",
                    shell=True
                )
                == 0
        ):
            self.info(self.docs.__name__)
        return 0

    def build(self, version: str = PYTHON_DEFAULT_VERSION, quiet: bool = True, rm: bool = False) -> Path | None:
        """Build a project `venv`, `completions`, `docs` and `clean`.

        Arguments:
            version: python version (default: PYTHON_DEFAULT_VERSION)
            quiet: quiet mode (default: True)
            rm: remove cache
        """
        # HACER: el pth sale si execute en terminal pero no en run
        ContextVar("NODEPS_QUIET").set(quiet)

        if not self.pyproject_toml.file:
            return None
        self.venv(version=version, quiet=quiet, rm=rm)
        self.completions()
        self.docs(quiet=quiet)
        self.clean()
        rv = subprocess.run(
            f"{self.executable(version=version)} -m build {self.root} --wheel",
            stdout=subprocess.PIPE,
            shell=True,
        )
        if rv.returncode != 0:
            sys.exit(rv.returncode)
        wheel = rv.stdout.splitlines()[-1].decode().split(" ")[2]
        if "py3-none-any.whl" not in wheel:
            raise CalledProcessError(completed=rv)
        self.info(
            f"{self.build.__name__}: {wheel}: {version}",
        )
        return self.root / "dist" / wheel

    def builds(self, quiet: bool = True, rm: bool = False) -> None:
        """Build a project `venv`, `completions`, `docs` and `clean`.

        Arguments:
            quiet: quiet mode (default: True)
            rm: remove cache
        """
        ContextVar("NODEPS_QUIET").set(quiet)

        if self.ci:
            self.build(quiet=quiet, rm=rm)
        else:
            for version in PYTHON_VERSIONS:
                self.build(version=version, quiet=quiet, rm=rm)

    def buildrequires(self) -> list[str]:
        """pyproject.toml build-system requires."""
        if self.pyproject_toml.file:
            return self.pyproject_toml.config.get("build-system", {}).get("requires", [])
        return []

    def clean(self) -> None:
        """Clean project."""
        if not in_tox():
            for item in self.clean_match:
                try:
                    for file in self.root.rglob(item):
                        if file.is_dir():
                            shutil.rmtree(self.root / item, ignore_errors=True)
                        else:
                            file.unlink(missing_ok=True)
                except FileNotFoundError:
                    pass

    def completions(self, uninstall: bool = False):
        """Generate completions to /usr/local/etc/bash_completion.d."""
        value = []

        if self.pyproject_toml.file:
            value = self.pyproject_toml.config.get("project", {}).get("scripts", {}).keys()
        elif d := self.distribution():
            value = [item.name for item in d.entry_points]
        if value:
            for item in value:
                if file := completions(item, uninstall=uninstall):
                    self.info(f"{self.completions.__name__}: {item} -> {file}")

    def coverage(self) -> int:
        """Runs coverage."""
        if (
                self.pyproject_toml.file
                and subprocess.check_call(f"{self.executable()} -m coverage run -m pytest {self.root}",
                                          shell=True) == 0
                and subprocess.check_call(f"{self.executable()} -m coverage report "
                                          f"--data-file={self.root}/reports/.coverage", shell=True) == 0
        ):
            self.info(self.coverage.__name__)
        return 0

    def dependencies(self) -> list[str]:
        """Dependencies from pyproject.toml or distribution."""
        if self.pyproject_toml.config:
            return self.pyproject_toml.config.get("project", {}).get("dependencies", [])
        if d := self.distribution():
            return [item for item in d.requires if "; extra" not in item]
        msg = f"Dependencies not found for {self.name=}"
        raise RuntimeWarning(msg)

    def distribution(self) -> importlib.metadata.Distribution | None:
        """Distribution."""
        return suppress(importlib.metadata.Distribution.from_name, self.name)

    def docker(self, quiet: bool = True) -> int:
        """Docker push.

        Arguments:
            quiet: quiet mode (default: True)
        """
        ContextVar("NODEPS_QUIET").set(quiet)

        rc = 0
        if not DOCKER and DOCKER_COMMAND and (dockerfile := self.root / "Dockerfile").is_file():
            for version in PYTHON_VERSIONS:
                tag = f"{GIT}/{self.name}:{version}"
                latest = f"-t {GIT}/{self.name}" if version == PYTHON_DEFAULT_VERSION else ""
                quiet = "--quiet" if quiet else ""
                command = (
                    f"docker build -f {dockerfile} {quiet} --build-arg='PY_VERSION={version}' "
                    f"-t {tag} {latest} {self.root}"
                )
                if rc := subprocess.run(command, stdout=subprocess.PIPE, shell=True).returncode != 0:
                    return rc
                latest = latest.strip("-t ")
                for image in [tag, latest]:
                    if image:
                        command = f"docker push {quiet} {image}"
                        if rc := subprocess.run(command, stdout=subprocess.PIPE, shell=True).returncode != 0:
                            return rc
                        self.info(f"{self.docker.__name__}: {image}")
        return int(rc)

    def docs(self, version: str = PYTHON_DEFAULT_VERSION, quiet: bool = True) -> int:
        """Build the documentation.

        Arguments:
            version: python version
            quiet: quiet mode (default: True)
        """
        ContextVar("NODEPS_QUIET").set(quiet)

        if not self.docsdir:
            return 0
        build_dir = self.docsdir / "_build"
        q = "-Q" if quiet else ""
        if build_dir.exists():
            shutil.rmtree(build_dir)

        if (
                subprocess.check_call(
                    f"{self.executable(version=version)} -m sphinx {q} --color {self.docsdir} {build_dir}",
                    shell=True,
                )
                == 0
        ):
            self.info(f"{self.docs.__name__}: {version}")
        return 0

    def executable(self, version: str = PYTHON_DEFAULT_VERSION) -> Path:
        """Executable."""
        return v / f"bin/python{version}" if (v := self.root / "venv").is_dir() and not self.ci else sys.executable

    @staticmethod
    def _extras(d):
        e = {}
        for item in d:
            if "; extra" in item:
                key = item.split("; extra == ")[1].replace("'", "").replace('"', "").removesuffix(" ")
                if key not in e:
                    e[key] = []
                e[key].append(item.split("; extra == ")[0].replace('"', "").removesuffix(" "))
        return e

    def extras(self, as_list: bool = False, rm: bool = False) -> dict[str, list[str]] | list[str]:
        """Optional dependencies from pyproject.toml or distribution.

        Examples:
            >>> import typer
            >>> from nodeps import Project
            >>>
            >>> nodeps = Project.nodeps()
            >>> nodeps.extras()  # doctest: +ELLIPSIS
            {'...': ['...
            >>> nodeps.extras(as_list=True)  # doctest: +ELLIPSIS
            ['...
            >>> Project(typer.__name__).extras()  # doctest: +ELLIPSIS
            {'all':...
            >>> Project("sampleproject").extras()  # doctest: +ELLIPSIS
            {'dev':...

        Args:
            as_list: return as list
            rm: remove cache

        Returns:
            dict or list
        """
        if self.pyproject_toml.config:
            e = self.pyproject_toml.config.get("project", {}).get("optional-dependencies", {})
        elif d := self.distribution():
            e = self._extras(d.requires)
        elif pypi := self.pypi(rm=rm):
            e = self._extras(pypi["info"]["requires_dist"])
        else:
            msg = f"Extras not found for {self.name=}"
            raise RuntimeWarning(msg)

        if as_list:
            return sorted({extra for item in e.values() for extra in item})
        return e

    @classmethod
    def nodeps(cls) -> Project:
        """Project Instance of nodeps."""
        return cls(__file__)

    def publish(
            self,
            part: Bump = Bump.PATCH,
            force: bool = False,
            ruff: bool = True,
            tox: bool = False,
            quiet: bool = True,
            rm: bool = False,
    ):
        """Publish runs runs `tests`, `commit`, `tag`, `push`, `twine` and `clean`.

        Args:
            part: part to increase if force
            force: force bump
            ruff: run ruff
            tox: run tox
            quiet: quiet mode (default: True)
            rm: remove cache
        """
        ContextVar("NODEPS_QUIET").set(quiet)

        self.tests(ruff=ruff, tox=tox, quiet=quiet)
        self.gh.commit()
        if (n := self.gh.next(part=part, force=force)) != (l := self.gh.latest()):
            self.gh.tag(n)
            self.gh.push()
            if rc := self.twine(rm=rm) != 0:
                sys.exit(rc)
            self.info(f"{self.publish.__name__}: {l} -> {n}")
            if rc := self.docker(quiet=quiet) != 0:
                sys.exit(rc)
        else:
            self.warning(f"{self.publish.__name__}: {n} -> nothing to do")

        self.clean()

    def pypi(
            self,
            rm: bool = False,
    ) -> dict[str, str | list | dict[str, str | list | dict[str, str | list]]]:
        """Pypi information for a package.

        Examples:
            >>> from nodeps import Project
            >>> from nodeps import NODEPS_PROJECT_NAME
            >>>
            >>> assert Project(NODEPS_PROJECT_NAME).pypi()["info"]["name"] == NODEPS_PROJECT_NAME

        Returns:
            dict: pypi information
            rm: use pickle cache or remove it.
        """
        return urljson(f"https://pypi.org/pypi/{self.name}/json", rm=rm)

    def pytest(self, version: str = PYTHON_DEFAULT_VERSION) -> int:
        """Runs pytest."""
        if self.pyproject_toml.file:
            rc = subprocess.run(f"{self.executable(version=version)} -m pytest {self.root}", shell=True).returncode
            self.info(f"{self.pytest.__name__}: {version}")
            return rc
        return 0

    def pytests(self) -> int:
        """Runs pytest for all versions."""
        rc = 0
        if self.ci:
            rc = self.pytest()
        else:
            for version in PYTHON_VERSIONS:
                rc = self.pytest(version=version)
                if rc != 0:
                    sys.exit(rc)
        return rc

    @classmethod
    def repos(
            cls,
            ret: ProjectRepos = ProjectRepos.NAMES,
            sync: bool = False,
            archive: bool = False,
            rm: bool = False,
    ) -> list[Path] | list[str] | dict[str, Project | str] | None:
        """Repo paths, names or Project instances under home, Archive or parent of nodeps top.

        Examples:
            >>> from nodeps import Project
            >>> from nodeps import NODEPS_PROJECT_NAME, Path, NODEPS_TOP, NODEPS_PATH
            >>>
            >>> assert NODEPS_PROJECT_NAME in Project.repos()
            >>> assert NODEPS_PROJECT_NAME in Project.repos(ProjectRepos.DICT)
            >>> assert NODEPS_PROJECT_NAME in Project.repos(ProjectRepos.INSTANCES)
            >>> assert NODEPS_PROJECT_NAME in Project.repos(ProjectRepos.PY)
            >>>
            >>> shrc = Path.home() / "shrc/.git"
            >>> if shrc.is_dir():
            ...     assert "shrc" not in Project.repos(ProjectRepos.PY)
            ...     assert "shrc" in Project.repos()

        Args:
            ret: return names, paths, dict or instances
            sync: push or pull all repos
            archive: look for repos under ~/Archive
            rm: remove cache
        """
        if rm or not (rv := Path.pickle(name=cls.repos)):
            dev = home = Path.home()
            add = sorted(add.iterdir()) if (add := home / "Archive").is_dir() and archive else []
            dev = sorted(dev.iterdir()) if NODEPS_TOP and (dev := NODEPS_TOP.parent) != home else []
            rv = {
                ProjectRepos.DICT: {},
                ProjectRepos.INSTANCES: {},
                ProjectRepos.NAMES: [],
                ProjectRepos.PATHS: [],
                ProjectRepos.PY: {},
            }
            for path in add + dev + sorted(home.iterdir()):
                if path.is_dir() and (path / ".git").exists() and Gh(path).admin(rm=rm):
                    instance = cls(path)
                    name = path.name
                    rv[ProjectRepos.DICT] |= {name: path}
                    rv[ProjectRepos.INSTANCES] |= {name: instance}
                    rv[ProjectRepos.NAMES].append(name)
                    rv[ProjectRepos.PATHS].append(path)
                    if instance.pyproject_toml.file:
                        rv[ProjectRepos.PY] |= {name: instance}
            Path.pickle(name=cls.repos, data=rv, rm=rm)

        if not rv:
            rv = Path.pickle(name=cls.repos)

        if sync:
            for item in rv[ProjectRepos.INSTANCES].values():
                item.sync()
            return None
        return rv[ret]

    def requirement(
            self,
            version: str = PYTHON_DEFAULT_VERSION,
            install: bool = False,
            upgrade: bool = False,
            quiet: bool = True,
            rm: bool = False,
    ) -> list[str] | int:
        """Dependencies and optional dependencies from pyproject.toml or distribution."""
        ContextVar("NODEPS_QUIET").set(quiet)

        req = sorted({*self.dependencies() + self.extras(as_list=True, rm=rm)})
        req = [item for item in req if not item.startswith(f"{self.name}[")]
        if (install or upgrade) and req:
            upgrade = ["--upgrade"] if upgrade else []
            quiet = "-q" if quiet else ""
            rv = subprocess.check_call([self.executable(version), "-m", "pip", "install", quiet, *upgrade, *req])
            self.info(f"{self.requirements.__name__}: {version}")
            return rv
        return req

    def requirements(
            self,
            upgrade: bool = False,
            quiet: bool = True,
            rm: bool = False,
    ) -> None:
        """Install dependencies and optional dependencies from pyproject.toml or distribution for python versions."""
        ContextVar("NODEPS_QUIET").set(quiet)

        if self.ci:
            self.requirement(install=True, upgrade=upgrade, quiet=quiet, rm=rm)
        else:
            for version in PYTHON_VERSIONS:
                self.requirement(version=version, install=True, upgrade=upgrade, quiet=quiet, rm=rm)

    def ruff(self, version: str = PYTHON_DEFAULT_VERSION) -> int:
        """Runs ruff."""
        if self.pyproject_toml.file:
            rv = subprocess.run(f"{self.executable(version=version)} -m ruff check {self.root}", shell=True).returncode
            self.info(f"{self.ruff.__name__}: {version}")
            return rv
        return 0

    # HACER: delete all tags and pypi versions

    def test(
            self, version: str = PYTHON_DEFAULT_VERSION, ruff: bool = True, tox: bool = False, quiet: bool = True
    ) -> int:
        """Test project, runs `build`, `ruff`, `pytest` and `tox`.

        Arguments:
            version: python version
            ruff: run ruff (default: True)
            tox: run tox (default: True)
            quiet: quiet mode (default: True)
        """
        ContextVar("NODEPS_QUIET").set(quiet)

        self.build(version=version, quiet=quiet)
        if ruff and (rc := self.ruff(version=version) != 0):
            sys.exit(rc)

        if rc := self.pytest(version=version) != 0:
            sys.exit(rc)

        if tox and (rc := self.tox() != 0):
            sys.exit(rc)

        return rc

    def tests(self, ruff: bool = True, tox: bool = False, quiet: bool = True) -> int:
        """Test project, runs `build`, `ruff`, `pytest` and `tox` for all versions.

        Arguments:
            ruff: runs ruff
            tox: runs tox
            quiet: quiet mode (default: True)
        """
        ContextVar("NODEPS_QUIET").set(quiet)

        rc = 0
        if self.ci:
            rc = self.test(ruff=ruff, tox=tox, quiet=quiet)
        else:
            for version in PYTHON_VERSIONS:
                rc = self.test(version=version, ruff=ruff, tox=tox, quiet=quiet)
                if rc != 0:
                    sys.exit(rc)
        return rc

    def tox(self) -> int:
        """Runs tox."""
        if self.pyproject_toml.file and not self.ci:
            rv = subprocess.run(f"{self.executable()} -m tox --root {self.root}", shell=True).returncode
            self.info(self.tox.__name__)
            return rv
        return 0

    def twine(
            self,
            part: Bump = Bump.PATCH,
            force: bool = False,
            rm: bool = False,
    ) -> int:
        """Twine.

        Args:
            part: part to increase if force
            force: force bump
            rm: remove cache
        """
        pypi = d.version if (d := self.distribution()) else None

        if (
                self.pyproject_toml.file
                and (pypi != self.gh.next(part=part, force=force))
                and "Private :: Do Not Upload" not in self.pyproject_toml.config.get("project", {}).get("classifiers",
                                                                                                        [])
        ):
            c = f"{self.executable()} -m twine upload -u __token__  {self.build(rm=rm).parent}/*"
            rc = subprocess.run(c, shell=True).returncode
            if rc != 0:
                return rc

        return 0

    def version(self, rm: bool = True) -> str:
        """Version from pyproject.toml, tag, distribution or pypi.

        Args:
            rm: remove cache
        """
        if v := self.pyproject_toml.config.get("project", {}).get("version"):
            return v
        if self.gh.top() and (v := self.gh.latest()):
            return v
        if d := self.distribution():
            return d.version
        if pypi := self.pypi(rm=rm):
            return pypi["info"]["version"]
        msg = f"Version not found for {self.name=} {self.directory=}"
        raise RuntimeWarning(msg)

    def venv(
            self,
            version: str = PYTHON_DEFAULT_VERSION,
            clear: bool = False,
            upgrade: bool = False,
            quiet: bool = True,
            rm: bool = False,
    ) -> None:
        """Creates venv, runs: `write` and `requirements`.

        Args:
            version: python version
            clear: remove venv
            upgrade: upgrade packages
            quiet: quiet
            rm: remove cache
        """
        ContextVar("NODEPS_QUIET").set(quiet)

        version = "" if self.ci else version
        if not self.pyproject_toml.file:
            return
        if not self.root:
            msg = f"Undefined: {self.root=} for {self.name=} {self.directory=}"
            raise RuntimeError(msg)
        self.write(rm=rm)
        if not self.ci:
            v = self.root / "venv"
            python = f"python{version}"
            clear = "--clean" if clear else ""
            subprocess.check_call(f"{python} -m venv {v} --prompt '.' {clear} --upgrade-deps --upgrade", shell=True)
            self.info(f"{self.venv.__name__}: {version}")
        self.requirement(version=version, install=True, upgrade=upgrade, quiet=quiet, rm=rm)

    def venvs(
            self,
            upgrade: bool = False,
            quiet: bool = True,
            rm: bool = False,
    ):
        """Installs venv for all python versions in :data:`PYTHON_VERSIONS`."""
        ContextVar("NODEPS_QUIET").set(quiet)

        if self.ci:
            self.venv(upgrade=upgrade, quiet=quiet, rm=rm)
        else:
            for version in PYTHON_VERSIONS:
                self.venv(version=version, upgrade=upgrade, quiet=quiet, rm=rm)

    def write(self, rm: bool = False):  # noqa: PLR0912, PLR0915
        """Updates setup.cfg (cmdclass, scripts), pyproject.toml and docs conf.py.

        [options.data_files]
        bin =
            bin/*
        ;/etc/gitconfig =
        ;    .gitconfig
        ;/etc/profile.d =
        ;    lib/*
        ;etc/gh =
        ;    gh/*

        Args:
            rm: remove cache
        """
        setup_cfg = self.root / "setup.cfg"
        if self.root and self.pyproject_toml.file and not setup_cfg.is_file():
            setup_cfg.touch()
        if self.root and setup_cfg.is_file():
            config = ConfigParser()
            config.read(setup_cfg)

            changed = False
            if (bindir := self.root / "bin").is_dir():
                scripts = config.getlist()
                new_scripts = [str(item.relative(self.root)) for item in sorted(bindir.iterdir()) if
                               not item.name.startswith(".")]
                if new_scripts != scripts:
                    changed = True
                    config.setlist(value=new_scripts)

            cmdclass = config.getlist(option="cmdclass")
            new_cmdclass = [
                f"build_py = {NODEPS_PROJECT_NAME}.BuildPy",
                f"develop = {NODEPS_PROJECT_NAME}.Develop",
                f"easy_install = {NODEPS_PROJECT_NAME}.EasyInstall",
                f"install_lib = {NODEPS_PROJECT_NAME}.InstallLib",
            ]
            if new_cmdclass != cmdclass:
                changed = True
                config.setlist(option="cmdclass", value=new_cmdclass)

            options = [
                ("options.package_data", self.name, "*.pth"),
                ("options.package_data", f"{self.name}.data", "*"),
                ("options", "package_dir", "= src"),
            ]
            for item in options:
                section_name = item[0]
                option = item[1]
                option_value_item = item[2]
                if not config.has_section(section_name):
                    changed = True
                    config.add_section(section_name)

                if config.has_option(section_name, option):
                    option_value = config.getlist(section_name, option)
                    if option_value_item not in option_value:
                        option_value.insert(0, option_value_item)
                        config.setlist(section_name, option, option_value)
                        changed = True
                else:
                    config.setlist(section_name, option, [option_value_item])
                    changed = True

            options = [
                ("global", "quiet", "1"),
                ("global", "verbose", "0"),
                ("global", "show_warnings", "false"),
                ("egg_info", "egg_base", "/tmp"),  # noqa: S108
                ("options", "include_package_data", "True"),
                ("options", "packages", "find:"),
                ("options.packages.find", "where", "src"),
            ]
            for item in options:
                section_name = item[0]
                option = item[1]
                option_value_item = item[2]
                if not config.has_section(section_name):
                    changed = True
                    config.add_section(section_name)

                if not config.has_option(section_name, option):
                    config.set(section_name, option, option_value_item)
                    changed = True

            if changed is True:
                with setup_cfg.open(mode="w", encoding="utf-8") as cfgfile:
                    config.write(cfgfile)
                self.info(f"{self.write.__name__}: {setup_cfg}")

        if self.pyproject_toml.file:
            original_project = copy.deepcopy(self.pyproject_toml.config.get("project", {}))
            github = self.gh.github(rm=rm)
            project = {
                "name": github["name"],
                "authors": [
                    {"name": AUTHOR, "email": EMAIL},
                ],
                "description": github.get("description", ""),
                "urls": {"Homepage": github["html_url"], "Documentation": f"https://{self.name}.readthedocs.io"},
                "dynamic": ["version"],
                "license": {"text": "MIT"},
                "readme": "README.md",
                "requires-python": f">={PYTHON_DEFAULT_VERSION}",
            }
            if "project" not in self.pyproject_toml.config:
                self.pyproject_toml.config["project"] = {}
            for key, value in project.items():
                if key not in self.pyproject_toml.config["project"]:
                    self.pyproject_toml.config["project"][key] = value

            self.pyproject_toml.config["project"] = dict_sort(self.pyproject_toml.config["project"])
            if original_project != self.pyproject_toml.config["project"]:
                with self.pyproject_toml.file.open("w") as f:
                    with pipmetapathfinder():
                        import tomlkit

                        tomlkit.dump(self.pyproject_toml.config, f)
                    self.info(f"{self.write.__name__}: {self.pyproject_toml.file}")

            if self.docsdir:
                imp = f"import {NODEPS_PROJECT_NAME}.__main__" if self.name == NODEPS_PROJECT_NAME else ""
                conf = f"""import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
{imp}
project = "{github["name"]}"
author = "{AUTHOR}"
# noinspection PyShadowingBuiltins
copyright = "{datetime.datetime.now().year}, {AUTHOR}"
extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.extlinks",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx_click",
    "sphinx.ext.intersphinx",
]
autoclass_content = "both"
autodoc_default_options = {{"members": True, "member-order": "bysource",
                           "undoc-members": True, "show-inheritance": True}}
autodoc_typehints = "description"
autosectionlabel_prefix_document = True
html_theme = "furo"
html_title, html_last_updated_fmt = "{self.name} docs", "%Y-%m-%dT%H:%M:%S"
inheritance_alias = {{}}
nitpicky = True
nitpick_ignore = [('py:class', '*')]
toc_object_entries = True
toc_object_entries_show_parents = "all"
pygments_style, pygments_dark_style = "sphinx", "monokai"
extlinks = {{
    "issue": ("https://github.com/{GIT}/{self.name}/issues/%s", "#%s"),
    "pull": ("https://github.com/{GIT}/{self.name}/pull/%s", "PR #%s"),
    "user": ("https://github.com/%s", "@%s"),
}}
intersphinx_mapping = {{
    "python": ("https://docs.python.org/3", None),
    "packaging": ("https://packaging.pypa.io/en/latest", None),
}}
"""  # noqa: DTZ005
                file = self.docsdir / "conf.py"
                original = file.read_text() if file.is_file() else ""
                if original != conf:
                    file.write_text(conf)
                    self.info(f"{self.write.__name__}: {file}")

                requirements = """click
furo >=2023.9.10, <2024
linkify-it-py >=2.0.2, <3
myst-parser >=2.0.0, <3
sphinx >=7.2.6, <8
sphinx-autobuild >=2021.3.14, <2022
sphinx-click >=5.0.1, <6
sphinx_autodoc_typehints
sphinxcontrib-napoleon >=0.7, <1
"""
                file = self.docsdir / "requirements.txt"
                original = file.read_text() if file.is_file() else ""
                if original != requirements:
                    file.write_text(requirements)
                    self.info(f"{self.write.__name__}: {file}")

                reference = f"""# Reference

## {self.name}

```{{eval-rst}}
.. automodule:: {self.name}
   :members:
```
"""
                file = self.docsdir / "reference.md"
                original = file.read_text() if file.is_file() else ""
                if original != reference:
                    file.write_text(reference)
                    self.info(f"{self.write.__name__}: {file}")
