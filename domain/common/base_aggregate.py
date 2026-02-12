class BaseAggregate:

    def __init__(self, aggregate_id):
        self.id = aggregate_id
        self.version = 0
        self._uncommitted_events = []

    # ============================================================
    # Internal event application
    # ============================================================

    def _apply(self, event):
        """
        Applies event to aggregate state.
        Used both for new events and replay.
        """
        handler_name = f"_apply_{event.__class__.__name__}"
        handler = getattr(self, handler_name, None)

        if handler is None:
            raise NotImplementedError(
                f"{self.__class__.__name__} does not implement {handler_name}"
            )

        handler(event)
        self.version += 1

    # ============================================================
    # Uncommitted events
    # ============================================================

    def _add_uncommitted_event(self, event):
        self._uncommitted_events.append(event)

    def get_uncommitted_events(self):
        return list(self._uncommitted_events)

    def clear_uncommitted_events(self):
        self._uncommitted_events.clear()

    # ============================================================
    # Replay
    # ============================================================

    def replay(self, events):
        """
        Rebuild aggregate from history.
        """
        for event in events:
            self._apply(event)

        # replay does not produce new events
        self.clear_uncommitted_events()