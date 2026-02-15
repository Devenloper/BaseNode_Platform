# infrastructure/outbox/dispatcher.py

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from infrastructure.db.models import OutboxRecord


class OutboxDispatcher:

    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        projector,
        batch_size: int = 1,  # must stay 1 for tests
    ):
        self._session_factory = session_factory
        self._projector = projector
        self._batch_size = batch_size

    async def dispatch_batch(self) -> int:

        async with self._session_factory() as session:

            result = await session.execute(
                select(OutboxRecord)
                .where(OutboxRecord.processed_at.is_(None))
                .order_by(OutboxRecord.id.asc())
                .limit(self._batch_size)
            )

            records = result.scalars().all()

            if not records:
                return 0

            now = datetime.now(timezone.utc)

            processed = 0

            for record in records:

                #
                # CRITICAL: projector contract (dispatcher mode)
                #
                await self._projector.project(
                    session=session,
                    event_type=record.event_type,
                    payload=record.payload,
                    aggregate_version=record.aggregate_version,
                )

                #
                # CRITICAL: mark processed AFTER successful projection
                #
                record.processed_at = now

                processed += 1

            #
            # CRITICAL: persist processed_at
            #
            await session.commit()

            return processed