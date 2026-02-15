from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID


# ==========================================================
# Frozen semantic base class (ADR-compliant)
# ==========================================================

class DomainEvent:
    """
    Semantically frozen Domain Event.

    Allows version injection ONLY.
    Prevents modification of business fields after creation.
    """

    __slots__ = ("version", "_initialized")

    version: int | None

    def __setattr__(self, name, value):

        # allow version injection anytime
        if name == "version":
            object.__setattr__(self, name, value)
            return

        # allow initialization phase
        if not hasattr(self, "_initialized"):
            object.__setattr__(self, name, value)
            return

        # block everything else
        raise AttributeError(f"{self.__class__.__name__} is immutable")

    def _freeze(self):
        object.__setattr__(self, "_initialized", True)


# ==========================================================
# Events
# ==========================================================

@dataclass(slots=True)
class StayCheckedIn(DomainEvent):

    stay_id: UUID
    room_id: str
    started_at: datetime
    version: int | None = field(default=None, compare=False)

    def __post_init__(self):
        self._freeze()

    def to_dict(self) -> dict:
        return {
            "stay_id": str(self.stay_id),
            "room_id": self.room_id,
            "started_at": self.started_at.isoformat(),
        }


@dataclass(slots=True)
class StayCheckedOut(DomainEvent):

    stay_id: UUID
    ended_at: datetime
    version: int | None = field(default=None, compare=False)

    def __post_init__(self):
        self._freeze()

    def to_dict(self) -> dict:
        return {
            "stay_id": str(self.stay_id),
            "ended_at": self.ended_at.isoformat(),
        }


@dataclass(slots=True)
class StayRelocated(DomainEvent):

    stay_id: UUID
    new_room_id: str
    relocated_at: datetime
    version: int | None = field(default=None, compare=False)

    def __post_init__(self):
        self._freeze()

    def to_dict(self) -> dict:
        return {
            "stay_id": str(self.stay_id),
            "new_room_id": self.new_room_id,
            "relocated_at": self.relocated_at.isoformat(),
        }