# infrastructure/db/repository.py

from infrastructure.db.event_store import SqlAlchemyEventStore
from infrastructure.db.outbox import OutboxStore


class SqlAlchemyRepository:
    """
    Event-sourced repository.

    - Uses EventStore
    - Uses Transactional Outbox
    - No commit
    - Replay through Domain
    """

    def __init__(self, session):
        self._session = session
        self._event_store = SqlAlchemyEventStore(session)
        self._outbox = OutboxStore(session)

    async def load(self, aggregate_cls, aggregate_id):
        """
        Restore aggregate via deterministic replay.
        """

        records = await self._event_store.load(aggregate_id)

        if not records:
            return None

        aggregate = aggregate_cls(aggregate_id)

        # Transform DB records into domain events
        domain_events = [
            aggregate_cls.event_from_record(record)
            for record in records
        ]

        aggregate.replay(domain_events)

        return aggregate

    async def save(self, aggregate, expected_version: int, metadata: dict):
        """
        Save aggregate changes (events + outbox) atomically.
        """

        events = aggregate.get_uncommitted_events()

        if not events:
            return

        await self._event_store.append(
            aggregate_id=aggregate.id,
            aggregate_type=aggregate.__class__.__name__,
            events=events,
            expected_version=expected_version,
            metadata=metadata,
        )

        # Добавляем в outbox те же записи
        records = await self._event_store.load(aggregate.id)
        await self._outbox.append(records[-len(events):])

        aggregate.clear_uncommitted_events()