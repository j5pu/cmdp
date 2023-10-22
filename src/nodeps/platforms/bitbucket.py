"""Bitbucket Platform."""
import dataclasses
from typing import ClassVar

from .base import BasePlatform


@dataclasses.dataclass
class BitbucketPlatform(BasePlatform):
    """Bitbucket platform."""
    PATTERNS: ClassVar[dict[str, str]] = {
        "https": (
            r"(?P<protocols>(git\+)?(?P<protocol>https))://(?P<_user>.+)@(?P<domain>.+?)"
            r"(?P<pathname>/(?P<owner>.+)/(?P<repo>.+?)(?:\.git)?)$"
        ),
        "ssh": (
            r"(?P<protocols>(git\+)?(?P<protocol>ssh))?(://)?git@(?P<domain>.+?):"
            r"(?P<pathname>(?P<owner>.+)/(?P<repo>.+?)(?:\.git)?)$"
        ),
    }
    FORMATS: ClassVar[dict[str, str]] = {
        "https": r"https://%(owner)s@%(domain)s/%(owner)s/%(repo)s%(dot_git)s",
        "ssh": r"git@%(domain)s:%(owner)s/%(repo)s%(dot_git)s",
    }
    DOMAINS = ("bitbucket.org",)
    DEFAULTS: ClassVar[dict[str, str]] = {"_user": "git"}
