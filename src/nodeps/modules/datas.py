"""DataClasses Module."""
__all__ = (
    "IdName",
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
class IdName:
    """Id and Name dataclass."""
    id: int  # noqa: A003
    name: str


@dataclasses.dataclass
class GroupUser:
    """GroupUser class."""
    group: IdName
    user: IdName
