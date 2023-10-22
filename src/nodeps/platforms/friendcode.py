"""FriendCode Platform."""
import dataclasses
from typing import ClassVar

from .base import BasePlatform


@dataclasses.dataclass
class FriendCodePlatform(BasePlatform):
    """FriendCode platform."""
    DOMAINS = ("friendco.de",)
    PATTERNS: ClassVar[dict[str, str]]  = {
        "https": (
            r"(?P<protocols>(git\+)?(?P<protocol>https))://(?P<domain>.+?)/"
            r"(?P<pathname>(?P<owner>.+)@user/(?P<repo>.+)).git"
        ),
    }
    FORMATS: ClassVar[dict[str, str]]  = {
        "https": r"https://%(domain)s/%(owner)s@user/%(repo)s%(dot_git)s",
    }
