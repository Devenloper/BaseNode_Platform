from typing import Any, Dict, List
from uuid import UUID


class DomainError(Exception):
    """Base domain error for aggregate violations."""
    pass


class BaseAggregate:
    """
    Core Event-Sourced Aggregate base class.

    Implements:
    - version semantics
    - handler dispatch table
    - uncommitted events contract
    - deterministic replay
    """

    def __init__(self, aggregate_id: UUID):
        self.id: UUID = aggregate_id

        # Event-sourcing internals
        self._version: int = 0
        self._uncommitted_events: List[Any] = []

        # Must be defined by concrete aggregate
        self._handlers: Dict[type, callable] = {}

    # ========================================================
    # Event Sourcing Core
    # ========================================================

    @property
    def version(self) -> int:
        return self._version

    def apply(self, event: Any) -> None:
        handler = self._handlers.get(type(event))
        if handler is None:
            raise DomainError(f"No handler for event {type(event)}")

        handler(event)
        self._version += 1

    def replay(self, events: List[Any]) -> None:
        for event in events:
            self.apply(event)

    def _record_event(self, event: Any) -> None:
        self.apply(event)
        self._uncommitted_events.append(event)

    # ========================================================
    # Uncommitted Events Contract
    # ========================================================

    def get_uncommitted_events(self) -> List[Any]:
        return list(self._uncommitted_events)

    def clear_uncommitted_events(self) -> None:
        self._uncommitted_events.clear()