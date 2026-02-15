from __future__ import annotations

from datetime import datetime
from uuid import UUID

from domain.common.base_aggregate import BaseAggregate

from .events import (
    StayCheckedIn,
    StayCheckedOut,
    StayRelocated,
)


class Stay(BaseAggregate):
    """
    Stay aggregate root.

    Event-sourced aggregate.

    State changes only through events.
    """

    def __init__(self, stay_id: UUID) -> None:
        super().__init__(stay_id)

        # read model state (derived from events)
        self.room_id: str | None = None
        self.started_at: datetime | None = None
        self.ended_at: datetime | None = None

        # infrastructure/tests expect this exact field name
        self._is_active: bool = False

    # ============================================================
    # Commands
    # ============================================================

    def check_in(
        self,
        room_id: str,
        started_at: datetime,
    ) -> None:
        """
        Check-in guest.

        Creates StayCheckedIn event.
        """

        if started_at.tzinfo is None:
            raise ValueError("started_at must be timezone-aware")

        if self._is_active:
            raise ValueError("Stay already active")

        event = StayCheckedIn(
            stay_id=self.id,
            room_id=room_id,
            started_at=started_at,
        )

        self._apply(event)
        self._add_uncommitted_event(event)

    def check_out(
        self,
        ended_at: datetime,
    ) -> None:
        """
        Check-out guest.

        Creates StayCheckedOut event.
        """

        if ended_at.tzinfo is None:
            raise ValueError("ended_at must be timezone-aware")

        if not self._is_active:
            raise ValueError("Stay not active")

        event = StayCheckedOut(
            stay_id=self.id,
            ended_at=ended_at,
        )

        self._apply(event)
        self._add_uncommitted_event(event)

    def relocate(
        self,
        new_room_id: str,
        relocated_at: datetime,
    ) -> None:
        """
        Relocate guest to another room.

        Creates StayRelocated event.
        """

        if relocated_at.tzinfo is None:
            raise ValueError("relocated_at must be timezone-aware")

        if not self._is_active:
            raise ValueError("Stay not active")

        event = StayRelocated(
            stay_id=self.id,
            new_room_id=new_room_id,
            relocated_at=relocated_at,
        )

        self._apply(event)
        self._add_uncommitted_event(event)

    # ============================================================
    # Event handlers
    # ============================================================

    def _apply_StayCheckedIn(self, event: StayCheckedIn) -> None:  # noqa: N802
        self.room_id = event.room_id
        self.started_at = event.started_at
        self.ended_at = None
        self._is_active = True

    def _apply_StayCheckedOut(self, event: StayCheckedOut) -> None:  # noqa: N802
        self.ended_at = event.ended_at
        self._is_active = False

    def _apply_StayRelocated(self, event: StayRelocated) -> None:  # noqa: N802
        self.room_id = event.new_room_id

    # ============================================================
    # EventStore reconstruction
    # ============================================================

    @staticmethod
    def event_from_record(record):
        """
        Reconstruct domain event from EventStore record.
        Infrastructure injects version.
        """

        payload = record.payload

        if record.event_type == "StayCheckedIn":

            event = StayCheckedIn(
                stay_id=UUID(payload["stay_id"]),
                room_id=payload["room_id"],
                started_at=datetime.fromisoformat(payload["started_at"]),
            )

        elif record.event_type == "StayCheckedOut":

            event = StayCheckedOut(
                stay_id=UUID(payload["stay_id"]),
                ended_at=datetime.fromisoformat(payload["ended_at"]),
            )

        elif record.event_type == "StayRelocated":

            event = StayRelocated(
                stay_id=UUID(payload["stay_id"]),
                new_room_id=payload["new_room_id"],
                relocated_at=datetime.fromisoformat(payload["relocated_at"]),
            )

        else:
            raise ValueError(f"Unknown event type: {record.event_type}")

        # inject version from EventStore
        if hasattr(record, "aggregate_version"):
            object.__setattr__(event, "version", record.aggregate_version)

        return event