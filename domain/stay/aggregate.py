from datetime import datetime
from typing import List, Type, Dict, Callable, Any
from uuid import UUID

from domain.common.base_aggregate import BaseAggregate

from .events import (
    StayCheckedIn,
    StayCheckedOut,
    StayRelocated,
    StayConflictDetected,
)


# ============================================================
# Exceptions
# ============================================================


class StayDomainError(Exception):
    pass

class StayAlreadyCheckedInError(StayDomainError):
    pass


class StayNotStartedError(StayDomainError):
    pass


class StayAlreadyCheckedOutError(StayDomainError):
    pass


class StayCompletedError(StayDomainError):
    pass


class InvalidStayPeriodError(StayDomainError):
    pass


class InvalidRelocationError(StayDomainError):
    pass


# ============================================================
# Lifecycle (ADR-0006)
# ============================================================


class StayLifecycle:
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"


# ============================================================
# Aggregate
# ============================================================


class Stay(BaseAggregate):

    def __init__(self, stay_id: UUID):
        self.id: UUID = stay_id

        self.lifecycle: str = StayLifecycle.NOT_STARTED
        self.room_id: UUID | None = None
        self.started_at: datetime | None = None
        self.ended_at: datetime | None = None
        self.conflict_detected: bool = False

        self._version: int = 0
        self._uncommitted_events: List[Any] = []

        self._handlers: Dict[Type, Callable] = {
            StayCheckedIn: self._apply_checked_in,
            StayCheckedOut: self._apply_checked_out,
            StayRelocated: self._apply_relocated,
            StayConflictDetected: self._apply_conflict_detected,
        }

    # ========================================================
    # Public API (Commands)
    # ========================================================

    def check_in(self, room_id: UUID, started_at: datetime) -> None:
        if self.lifecycle != StayLifecycle.NOT_STARTED:
            raise StayAlreadyCheckedInError()

        event = StayCheckedIn(
            stay_id=self.id,
            room_id=room_id,
            started_at=started_at,
        )

        self._record_event(event)

    def check_out(self, ended_at: datetime) -> None:
        if self.lifecycle == StayLifecycle.NOT_STARTED:
            raise StayNotStartedError()

        if self.lifecycle == StayLifecycle.COMPLETED:
            raise StayAlreadyCheckedOutError()

        if self.started_at is None:
            raise StayDomainError("Invalid internal state")

        if ended_at <= self.started_at:
            raise InvalidStayPeriodError()

        event = StayCheckedOut(
            stay_id=self.id,
            ended_at=ended_at,
        )

        self._record_event(event)

    def relocate(self, new_room_id: UUID, relocated_at: datetime) -> None:
        if self.lifecycle == StayLifecycle.NOT_STARTED:
            raise StayNotStartedError()

        if self.lifecycle == StayLifecycle.COMPLETED:
            raise StayCompletedError()

        if self.room_id == new_room_id:
            raise InvalidRelocationError()

        event = StayRelocated(
            stay_id=self.id,
            new_room_id=new_room_id,
            relocated_at=relocated_at,
        )

        self._record_event(event)

    def detect_conflict(self, reason: str, detected_at: datetime) -> None:
        event = StayConflictDetected(
            stay_id=self.id,
            reason=reason,
            detected_at=detected_at,
        )

        self._record_event(event)

    # ========================================================
    # Event Sourcing Core
    # ========================================================

    def apply(self, event: Any) -> None:
        handler = self._handlers.get(type(event))
        if handler is None:
            raise StayDomainError(f"No handler for {type(event)}")

        handler(event)

        self._version += 1

    def replay(self, events: List[Any]) -> None:
        for event in events:
            self.apply(event)

    def _record_event(self, event: Any) -> None:
        self.apply(event)
        self._uncommitted_events.append(event)

    def get_uncommitted_events(self) -> List[Any]:
        return list(self._uncommitted_events)

    def clear_uncommitted_events(self) -> None:
        self._uncommitted_events.clear()

    # ========================================================
    # Apply Handlers
    # ========================================================

    def _apply_checked_in(self, event: StayCheckedIn) -> None:
        self.lifecycle = StayLifecycle.IN_PROGRESS
        self.room_id = event.room_id
        self.started_at = event.started_at

    def _apply_checked_out(self, event: StayCheckedOut) -> None:
        self.lifecycle = StayLifecycle.COMPLETED
        self.ended_at = event.ended_at

    def _apply_relocated(self, event: StayRelocated) -> None:
        self.room_id = event.new_room_id

    def _apply_conflict_detected(self, event: StayConflictDetected) -> None:
        self.conflict_detected = True