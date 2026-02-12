from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


# ============================================================
# StayCheckedIn
# ============================================================

@dataclass(frozen=True)
class StayCheckedIn:
    stay_id: UUID
    room_id: str
    started_at: datetime

    def to_dict(self) -> dict:
        return {
            "stay_id": str(self.stay_id),
            "room_id": self.room_id,
            "started_at": self.started_at.isoformat(),
        }


# ============================================================
# StayCheckedOut
# ============================================================

@dataclass(frozen=True)
class StayCheckedOut:
    stay_id: UUID
    ended_at: datetime

    def to_dict(self) -> dict:
        return {
            "stay_id": str(self.stay_id),
            "ended_at": self.ended_at.isoformat(),
        }


# ============================================================
# StayRelocated
# ============================================================

@dataclass(frozen=True)
class StayRelocated:
    stay_id: UUID
    new_room_id: str
    relocated_at: datetime

    def to_dict(self) -> dict:
        return {
            "stay_id": str(self.stay_id),
            "new_room_id": self.new_room_id,
            "relocated_at": self.relocated_at.isoformat(),
        }