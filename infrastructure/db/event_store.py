# infrastructure/db/event_store.py

from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError

from application.exceptions import VersionConflictError
from infrastructure.db.models import EventRecord


class SqlAlchemyEventStore:
    """
    Append-only Event Store.

    - No UPDATE
    - No DELETE
    - No commit
    - Optimistic locking
    """

    def __init__(self, session):
        self._session = session

    async def append(
        self,
        aggregate_id,
        aggregate_type: str,
        events: list,
        expected_version: int,
        metadata: dict,
    ):
        """
        Append events with optimistic locking.
        Atomic within UnitOfWork transaction.
        """

        # 1️⃣ Получаем текущую версию агрегата
        stmt = (
            select(func.coalesce(func.max(EventRecord.aggregate_version), 0))
            .where(EventRecord.aggregate_id == str(aggregate_id))
        )

        result = await self._session.execute(stmt)
        current_version = result.scalar_one()

        # 2️⃣ Optimistic locking check
        if current_version != expected_version:
            raise VersionConflictError(
                aggregate_id=aggregate_id,
                expected=expected_version,
                actual=current_version,
            )

        next_version = current_version

        # 3️⃣ Append events
        try:
            for event in events:
                next_version += 1

                record = EventRecord(
                    aggregate_id=str(aggregate_id),
                    aggregate_type=aggregate_type,
                    aggregate_version=next_version,
                    event_type=event.__class__.__name__,
                    payload=event.to_dict(),
                    event_metadata=metadata,
                )

                self._session.add(record)

        # 4️⃣ Race-condition protection (UNIQUE constraint)
        except IntegrityError:
            raise VersionConflictError(
                aggregate_id=aggregate_id,
                expected=expected_version,
                actual=current_version,
            )

    async def load(self, aggregate_id):
        """
        Load events ordered by aggregate_version (deterministic replay).
        """

        stmt = (
            select(EventRecord)
            .where(EventRecord.aggregate_id == str(aggregate_id))
            .order_by(EventRecord.aggregate_version.asc())
        )

        result = await self._session.execute(stmt)

        return result.scalars().all()