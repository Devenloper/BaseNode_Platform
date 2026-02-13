# infrastructure/db/outbox.py

from sqlalchemy.ext.asyncio import AsyncSession
from infrastructure.db.models import OutboxRecord


class OutboxStore:
    """
    Transactional Outbox.
    Работает в той же транзакции, что и EventStore.
    """

    def __init__(self, session: AsyncSession):
        self._session = session

    async def append(self, event_records):
        for record in event_records:
            outbox = OutboxRecord(
                aggregate_id=record.aggregate_id,
                aggregate_type=record.aggregate_type,
                aggregate_version=record.aggregate_version,
                event_type=record.event_type,
                payload=record.payload,
                event_metadata=record.event_metadata,
            )

            self._session.add(outbox)