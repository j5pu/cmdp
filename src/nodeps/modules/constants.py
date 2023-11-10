"""Constants Module."""
__all__ = (
    "AUTHOR",
    "CI",
    "DOCKER",
    "DOCKER_COMMAND",
    "EXECUTABLE",
    "EXECUTABLE_SITE",
    "GIT",
    "GIT_DEFAULT_SCHEME",
    "GITHUB_DOMAIN",
    "GITHUB_TOKEN",
    "GITHUB_URL",
    "LINUX",
    "LOCAL",
    "MACOS",
    "NODEPS_EXECUTABLE",
    "NODEPS_PIP_POST_INSTALL_FILENAME",
    "NODEPS_PROJECT_NAME",
    "NODEPS_PATH",
    "NODEPS_TOP",
    "PY_MAJOR_MINOR",
    "PYTHON_VERSIONS",
    "PYTHON_DEFAULT_VERSION",
    "SUDO",
    "USER",
    "EMAIL",
    "PW_ROOT",
    "PW_USER",
)

import os
import pathlib
import pwd
import shutil
import sys

AUTHOR = "José Antonio Puértolas Montañés"
CI = bool(os.environ.get("CI"))
"""True if running in CI."""
DOCKER = bool((_p := pathlib.Path("/proc/self/mountinfo")).is_file() and "/docker" in _p.read_text())
"""True if running inside container."""
DOCKER_COMMAND = bool(shutil.which("docker", mode=os.X_OK))
"""True if docker install."""
EXECUTABLE = pathlib.Path(sys.executable)
EXECUTABLE_SITE = pathlib.Path(EXECUTABLE).resolve()
GIT = os.environ.get("GIT", "j5pu")
"""GitHub user name"""
GIT_DEFAULT_SCHEME = "https"
GITHUB_DOMAIN = "github.com"
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", os.environ.get("GH_TOKEN", os.environ.get("TOKEN")))
"""GitHub Token"""
GITHUB_URL = {
    "api": f"https://api.{GITHUB_DOMAIN}",
    "git+file": "git+file://",
    "git+https": f"git+https://{GITHUB_DOMAIN}/",
    "git+ssh": f"git+ssh://git@{GITHUB_DOMAIN}/",
    "https": f"https://{GITHUB_DOMAIN}/",
    "ssh": f"git@{GITHUB_DOMAIN}:",
}
"""
GitHub: api, git+file, git+https, git+ssh, https, ssh and git URLs
(join directly the user or path without '/' or ':')
"""
LINUX = sys.platform == "linux"
"""Is Linux? sys.platform == 'linux'"""
LOCAL = not CI and not DOCKER
"""True if not running in CI nor DOCKER container."""
MACOS = sys.platform == "darwin"
"""Is macOS? sys.platform == 'darwin'"""
NODEPS_EXECUTABLE = "p"
"""NoDeps Executable Name"""
NODEPS_PATH = pathlib.Path(__file__).parent.parent
"""NoDeps Source Path: src/nodeps"""
NODEPS_PIP_POST_INSTALL_FILENAME = "_post_install.py"
"""Filename that will be searched after pip installs a package."""
NODEPS_PROJECT_NAME = "nodeps"
"""NoDeps Project Name"""
NODEPS_TOP = _p if ((_p := pathlib.Path(
    os.environ.get("GITHUB_WORKSPACE", NODEPS_PATH.parent.parent))) / ".git").exists() else None
"""NoDeps Git Repository Top if exists, else None."""
PY_MAJOR_MINOR = f"{sys.version_info[0]}.{sys.version_info[1]}"
"""Major.Minor Python running version."""
PYTHON_VERSIONS = (
    os.environ.get("PYTHON_DEFAULT_VERSION", "3.11"),
    "3.12",
)
"""Python versions for venv, etc."""
PYTHON_DEFAULT_VERSION = PYTHON_VERSIONS[0]
"""Python default version for venv, etc."""
SUDO = str(rv) if (rv := pathlib.Path("/usr/bin/sudo")).exists() else ""
"""Sudo command path if exists."""
USER = os.getenv("USER", "root")
""""Environment Variable $USER or root if not USER variable"""

EMAIL = f"63794670+{GIT}@users.noreply.github.com"
PW_ROOT = pwd.getpwnam("root")
PW_USER = pwd.getpwnam(USER)
