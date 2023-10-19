"""Assembla Platform."""
from typing import ClassVar

from .base import BasePlatform


class AssemblaPlatform(BasePlatform):
    """Assembla platform."""
    DOMAINS = ("git.assembla.com",)
    PATTERNS: ClassVar[dict[str, str]] = {
        "ssh": r"(?P<protocols>(git\+)?(?P<protocol>ssh))?(://)?git@(?P<domain>.+?):(?P<pathname>(?P<repo>.+)).git",
        "git": r"(?P<protocols>(?P<protocol>git))://(?P<domain>.+?)/(?P<pathname>(?P<repo>.+)).git",
    }
    FORMATS: ClassVar[dict[str, str]] = {
        "ssh": r"git@%(domain)s:%(repo)s%(dot_git)s",
        "git": r"git://%(domain)s/%(repo)s%(dot_git)s",
    }
    DEFAULTS: ClassVar[dict[str, str]] = {"_user": "git"}
