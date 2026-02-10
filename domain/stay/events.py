from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


# ============================================================
# Domain Events (Business data only)
# ============================================================


@dataclass(frozen=True)
class StayCheckedIn:
    stay_id: UUID
    room_id: UUID
    started_at: datetime


@dataclass(frozen=True)
class StayCheckedOut:
    stay_id: UUID
    ended_at: datetime


@dataclass(frozen=True)
class StayRelocated:
    stay_id: UUID
    new_room_id: UUID
    relocated_at: datetime


@dataclass(frozen=True)
class StayConflictDetected:
    stay_id: UUID
    reason: str
    detected_at: datetime