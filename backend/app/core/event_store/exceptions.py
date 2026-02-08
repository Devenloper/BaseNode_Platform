# event_store/exceptions.py

class EventStoreError(Exception):
    """Base Event Store exception."""


class ConcurrencyConflict(EventStoreError):
    """Aggregate version conflict detected."""


class IdempotencyConflict(EventStoreError):
    """Duplicate external_event_id detected."""


class DuplicateEventId(EventStoreError):
    """Duplicate event_id detected within tenant."""