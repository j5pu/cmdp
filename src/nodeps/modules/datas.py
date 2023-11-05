"""DataClasses Module."""
__all__ = (
    "GitStatus",
    "GroupUser",
)

import dataclasses


@dataclasses.dataclass
class GitStatus:
    """Git SHA and status.

    Attributes:
        base: base SHA
        dirty: is repository dirty including untracked files
        diverge: need push and pull. It considers is dirty.
        local: local SHA
        pull: needs pull
        push: needs push
        remote: remote SHA
    """
    base: str = ""
    dirty: bool = False
    diverge: bool = False
    local: str = ""
    pull: bool = False
    push: bool = False
    remote: str = ""


@dataclasses.dataclass
class GroupUser:
    """GroupUser class."""
    group: int | str
    user: int | str

