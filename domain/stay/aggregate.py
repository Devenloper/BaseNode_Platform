from uuid import UUID
from datetime import datetime
from typing import List

from domain.common.base_aggregate import BaseAggregate
from .events import (
    StayCheckedIn,
    StayCheckedOut,
    StayRelocated,
)


class Stay(BaseAggregate):

    # ============================================================
    # Constructor
    # ============================================================

    def __init__(self, stay_id: UUID):
        super().__init__(stay_id)

        self.room_id: str | None = None
        self.started_at: datetime | None = None
        self.ended_at: datetime | None = None
        self._is_active: bool = False

    # ============================================================
    # Public domain operations
    # ============================================================

    def check_in(self, *, room_id: str, started_at: datetime) -> None:

        if self._is_active:
            raise ValueError("Stay already active")

        self._validate_datetime(started_at, "started_at")

        event = StayCheckedIn(
            stay_id=self.id,
            room_id=room_id,
            started_at=started_at,
        )

        self._apply(event)
        self._add_uncommitted_event(event)

    def check_out(self, *, ended_at: datetime) -> None:

        if not self._is_active:
            raise ValueError("Cannot check out inactive stay")

        self._validate_datetime(ended_at, "ended_at")

        event = StayCheckedOut(
            stay_id=self.id,
            ended_at=ended_at,
        )

        self._apply(event)
        self._add_uncommitted_event(event)

    def relocate(self, *, new_room_id: str, relocated_at: datetime) -> None:

        if not self._is_active:
            raise ValueError("Cannot relocate inactive stay")

        self._validate_datetime(relocated_at, "relocated_at")

        event = StayRelocated(
            stay_id=self.id,
            new_room_id=new_room_id,
            relocated_at=relocated_at,
        )

        self._apply(event)
        self._add_uncommitted_event(event)

    # ============================================================
    # Apply handlers (Event Sourcing)
    # ============================================================

    def _apply_StayCheckedIn(self, event: StayCheckedIn) -> None:
        self.room_id = event.room_id
        self.started_at = event.started_at
        self._is_active = True

    def _apply_StayCheckedOut(self, event: StayCheckedOut) -> None:
        self.ended_at = event.ended_at
        self._is_active = False

    def _apply_StayRelocated(self, event: StayRelocated) -> None:
        self.room_id = event.new_room_id

    # ============================================================
    # Replay support
    # ============================================================

    @classmethod
    def event_from_record(cls, record):

        payload = record.payload

        if record.event_type == "StayCheckedIn":
            return StayCheckedIn(
                stay_id=UUID(payload["stay_id"]),
                room_id=payload["room_id"],
                started_at=datetime.fromisoformat(payload["started_at"]),
            )

        if record.event_type == "StayCheckedOut":
            return StayCheckedOut(
                stay_id=UUID(payload["stay_id"]),
                ended_at=datetime.fromisoformat(payload["ended_at"]),
            )

        if record.event_type == "StayRelocated":
            return StayRelocated(
                stay_id=UUID(payload["stay_id"]),
                new_room_id=payload["new_room_id"],
                relocated_at=datetime.fromisoformat(payload["relocated_at"]),
            )

        raise ValueError(f"Unknown event type: {record.event_type}")

    # ============================================================
    # Internal validation
    # ============================================================

    @staticmethod
    def _validate_datetime(value: datetime, field_name: str) -> None:
        if value.tzinfo is None:
            raise ValueError(f"{field_name} must be timezone-aware")