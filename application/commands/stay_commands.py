from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class CheckInStay:
    stay_id: UUID
    room_id: UUID
    started_at: datetime
    expected_version: int
    actor: str
    correlation_id: UUID
    causation_id: UUID


@dataclass(frozen=True)
class CheckOutStay:
    stay_id: UUID
    ended_at: datetime
    expected_version: int
    actor: str
    correlation_id: UUID
    causation_id: UUID


@dataclass(frozen=True)
class RelocateStay:
    stay_id: UUID
    new_room_id: UUID
    relocated_at: datetime
    expected_version: int
    actor: str
    correlation_id: UUID
    causation_id: UUID