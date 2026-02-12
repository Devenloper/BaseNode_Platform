from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.db.event_store import EventStore
from infrastructure.db.outbox import OutboxStore
from domain.common.base_aggregate import BaseAggregate


class SqlAlchemyRepository:
    """
    Infrastructure repository.

    ❗ Не содержит бизнес-логики.
    ❗ Не вычисляет version.
    ❗ Не управляет транзакцией.
    ❗ Не делает commit.

    Только orchestration записи в:
        - EventStore
        - Outbox
    """

    def __init__(self, session: AsyncSession):
        self._session = session
        self._event_store = EventStore(session)
        self._outbox = OutboxStore(session)

    # ---------------------------------------------------------
    # LOAD
    # ---------------------------------------------------------

    async def load(self, aggregate_cls, aggregate_id):
        """
        Восстановление агрегата через replay.
        """
        records = await self._event_store.load(aggregate_id)

        aggregate = aggregate_cls(aggregate_id)

        domain_events = [
            aggregate_cls.event_from_record(record)
            for record in records
        ]

        aggregate.replay(domain_events)

        return aggregate

    # ---------------------------------------------------------
    # SAVE
    # ---------------------------------------------------------

    async def save(
        self,
        aggregate: BaseAggregate,
        *,
        expected_version: int,
        metadata: dict,
    ):
        """
        Сохраняет агрегат через append-only.

        expected_version:
            Приходит из Application слоя.
            Repository НЕ вычисляет его.

        metadata:
            Приходит сверху (correlation_id, trace_id и т.д.)
        """

        events = aggregate.get_uncommitted_events()

        if not events:
            return []

        # Append в EventStore
        event_records = await self._event_store.append(
            aggregate_id=aggregate.id,
            aggregate_type=aggregate.__class__.__name__,
            events=events,
            expected_version=expected_version,
            event_metadata=metadata,
        )

        # Append в Outbox (в той же session)
        await self._outbox.append(event_records)

        # Очистка uncommitted
        aggregate.clear_uncommitted_events()

        return event_records