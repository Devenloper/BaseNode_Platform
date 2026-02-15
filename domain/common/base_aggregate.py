from __future__ import annotations

from typing import Any, List


class DomainError(Exception):
    """
    Base class for domain errors.
    Safe to expose outside domain.
    """
    pass


class BaseAggregate:
    """
    Base class for all aggregates.

    Contract required by tests and infrastructure.
    """

    def __init__(self, aggregate_id: Any):
        self.id = aggregate_id
        self.version: int = 0
        self._uncommitted_events: List[Any] = []

    # -------------------------
    # APPLY
    # -------------------------

    def _apply(self, event: Any) -> None:
        """
        Apply event to state and increment version.
        """
        handler_name = f"_apply_{event.__class__.__name__}"
        handler = getattr(self, handler_name, None)

        if handler is None:
            raise NotImplementedError(
                f"{self.__class__.__name__} does not implement {handler_name}"
            )

        handler(event)

        # CRITICAL: tests expect version increment here
        self.version += 1

    # -------------------------
    # ADD UNCOMMITTED EVENT
    # -------------------------

    def _add_uncommitted_event(self, event: Any) -> None:
        """
        Add event to uncommitted list.
        """
        self._uncommitted_events.append(event)

    # -------------------------
    # GET UNCOMMITTED EVENTS
    # -------------------------

    def get_uncommitted_events(self) -> List[Any]:
        return list(self._uncommitted_events)

    # -------------------------
    # CLEAR UNCOMMITTED EVENTS
    # -------------------------

    def clear_uncommitted_events(self) -> None:
        self._uncommitted_events.clear()

    # -------------------------
    # REPLAY
    # -------------------------

    def replay(self, events: List[Any]) -> None:
        """
        Replay events to rebuild state.
        """
        for event in events:
            self._apply(event)

        self.clear_uncommitted_events()