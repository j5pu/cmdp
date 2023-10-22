"""Assembla Platform."""
import dataclasses
from typing import ClassVar

from .base import BasePlatform


@dataclasses.dataclass
class AssemblaPlatform(BasePlatform):
    """Assembla platform."""
    DOMAINS = ("git.assembla.com",)
    PATTERNS: ClassVar[dict[str, str]] = {
        "git": r"(?P<protocols>(?P<protocol>git))://(?P<domain>.+?)/(?P<pathname>(?P<repo>.+)).git",
        "ssh": r"(?P<protocols>(git\+)?(?P<protocol>ssh))?(://)?git@(?P<domain>.+?):(?P<pathname>(?P<repo>.+)).git",
    }
    FORMATS: ClassVar[dict[str, str]] = {
        "git": r"git://%(domain)s/%(repo)s%(dot_git)s",
        "git+https": r"git+https://%(domain)s/%(owner)s/%(groups_slash)s%(repo)s%(dot_git)s%(path_raw)s",
        "git+ssh": r"git+ssh://git@%(domain)s/%(owner)s/%(groups_slash)s%(repo)s%(dot_git)s%(path_raw)s",
        "ssh": r"git@%(domain)s:%(repo)s%(dot_git)s",
    }
    DEFAULTS: ClassVar[dict[str, str]] = {"_user": "git"}
