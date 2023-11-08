"""GitHub platform."""
import dataclasses
from typing import ClassVar

from .base import BasePlatform


@dataclasses.dataclass
class GitHubPlatform(BasePlatform):
    """GitHub platform."""
    PATTERNS: ClassVar[dict[str, str]] = {
        "git": (
            r"(?P<protocols>(?P<protocol>git))://(?P<domain>.+?)"
            r"(?P<pathname>/(?P<owner>[^/]+)/(?P<repo>[^/]+?)(?:(\.git)?(/)?)"
            r"(?P<path_raw>(/blob/|/tree/).+)?)$"
        ),
        "https": (
            r"(?P<protocols>(git\+)?(?P<protocol>https))://"
            r"((?P<username>[^/]+?):(?P<access_token>[^/]+?)@)?(?P<domain>[^/]+?)"
            r"(?P<pathname>/(?P<owner>[^/]+?)/(?P<repo>[^/]+?)(?:(\.git)?(/)?)(?P<path_raw>(/blob/|/tree/).+)?)$"
        ),
        "ssh": (
            r"(?P<protocols>(git\+)?(?P<protocol>ssh))?(://)?git@(?P<domain>.+?)(?P<pathname>(:|/)"
            r"(?P<owner>[^/]+)/(?P<repo>[^/]+?)(?:(\.git)?(/)?)"
            r"(?P<path_raw>(/blob/|/tree/).+)?)$"
        ),
    }
    FORMATS: ClassVar[dict[str, str]] = {
        "git": r"git://%(domain)s/%(owner)s/%(repo)s%(dot_git)s%(path_raw)s",
        "git+https": r"git+https://%(domain)s/%(owner)s/%(repo)s%(dot_git)s%(path_raw)s",
        "git+ssh": r"git+ssh://git@%(domain)s/%(owner)s/%(repo)s%(dot_git)s%(path_raw)s",
        "https": r"https://%(domain)s/%(owner)s/%(repo)s%(dot_git)s%(path_raw)s",
        "ssh": r"git@%(domain)s:%(owner)s/%(repo)s%(dot_git)s%(path_raw)s",
    }
    DOMAINS = (
        "github.com",
        "gist.github.com",
    )
    DEFAULTS: ClassVar[dict[str, str]] = {"_user": "git"}

    @staticmethod
    def clean_data(data):
        """Clean data."""
        data = BasePlatform.clean_data(data)
        if data["path_raw"].startswith("/blob/"):
            data["path"] = data["path_raw"].replace("/blob/", "")
        if data["path_raw"].startswith("/tree/"):
            data["branch"] = data["path_raw"].replace("/tree/", "")
        return data
