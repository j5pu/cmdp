"""Gitlab URL."""
import dataclasses
from typing import ClassVar

from .base import BasePlatform


@dataclasses.dataclass
class GitLabPlatform(BasePlatform):
    """GitLab platform."""
    PATTERNS: ClassVar[dict[str, str]] = {
        "git": (
            r"(?P<protocols>(?P<protocol>git))://(?P<domain>[^:/]+):?(?P<port>[0-9]+)?(?(port))?"
            r"(?P<pathname>/(?P<owner>[^/]+?)/"
            r"(?P<groups_path>.*?)?(?(groups_path)/)?(?P<repo>[^/]+?)(?:(\.git)?(/)?)"
            r"(?P<path_raw>(/blob/|/-/blob/|/-/tree/).+)?)$"
        ),
        "https": (
            r"(?P<protocols>(git\+)?(?P<protocol>https))://"
            r"((?P<username>[^/]+?):(?P<access_token>[^/]+?)@)?(?P<domain>[^:/]+)(?P<port>:[0-9]+)?"
            r"(?P<pathname>/(?P<owner>[^/]+?)/"
            r"(?P<groups_path>.*?)?(?(groups_path)/)?(?P<repo>[^/]+?)(?:(\.git)?(/)?)"
            r"(?P<path_raw>(/blob/|/-/blob/|/-/tree/).+)?)$"
        ),
        "ssh": (
            r"(?P<protocols>(git\+)?(?P<protocol>ssh))?(://)?(?P<_user>.+?)"
            r"@(?P<domain>[^:/]+)(:)?(?P<port>[0-9]+)?(?(port))?"
            r"(?P<pathname>/?(?P<owner>[^/]+)/"
            r"(?P<groups_path>.*?)?(?(groups_path)/)?(?P<repo>[^/]+?)(?:(\.git)?(/)?)"
            r"(?P<path_raw>(/blob/|/-/blob/|/-/tree/).+)?)$"
        ),
    }
    FORMATS: ClassVar[dict[str, str]] = {
        "git": r"git://%(domain)s%(port)s/%(owner)s/%(groups_slash)s%(repo)s%(dot_git)s%(path_raw)s",
        "git+https": r"git+https://%(domain)s/%(owner)s/%(groups_slash)s%(repo)s%(dot_git)s%(path_raw)s",
        "git+ssh": r"git+ssh://git@%(domain)s/%(owner)s/%(groups_slash)s%(repo)s%(dot_git)s%(path_raw)s",
        "https": r"https://%(domain)s/%(owner)s/%(groups_slash)s%(repo)s%(dot_git)s%(path_raw)s",
        "ssh": r"git@%(domain)s:%(port_slash)s%(owner)s/%(groups_slash)s%(repo)s%(dot_git)s%(path_raw)s",
    }
    SKIP_DOMAINS = (
        "github.com",
        "gist.github.com",
    )
    DEFAULTS: ClassVar[dict[str, str]] = {"_user": "git", "port": ""}

    @staticmethod
    def clean_data(data):
        """Clean data."""
        data = BasePlatform.clean_data(data)
        if data["path_raw"].startswith("/blob/"):
            data["path"] = data["path_raw"].replace("/blob/", "")
        if data["path_raw"].startswith("/-/blob/"):
            data["path"] = data["path_raw"].replace("/-/blob/", "")
        if data["path_raw"].startswith("/-/tree/"):
            data["branch"] = data["path_raw"].replace("/-/tree/", "")
        return data
