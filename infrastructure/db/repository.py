from infrastructure.db.event_store import EventStore
from infrastructure.db.outbox import OutboxStore
from domain.common.base_aggregate import BaseAggregate


class SqlAlchemyRepository:

    def __init__(self, session):
        self._session = session
        self._event_store = EventStore(session)
        self._outbox = OutboxStore(session)

    async def load(self, aggregate_cls, aggregate_id):
        records = await self._event_store.load(aggregate_id)

        aggregate = aggregate_cls(aggregate_id)

        domain_events = [
            aggregate_cls.event_from_record(record)
            for record in records
        ]

        aggregate.replay(domain_events)

        return aggregate

    async def save(
        self,
        aggregate: BaseAggregate,
        *,
        expected_version: int,
        metadata: dict,
    ):
        # append в event_store
        event_records = await self._event_store.append(
            aggregate_id=aggregate.id,
            aggregate_type=aggregate.__class__.__name__,
            events=aggregate.get_uncommitted_events(),
            expected_version=expected_version,
            metadata=metadata,
        )

        # append в outbox (та же session)
        await self._outbox.append(event_records)

        # очистка uncommitted
        aggregate.clear_uncommitted_events()

        return event_records