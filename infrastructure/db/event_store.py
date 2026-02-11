from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from .models import EventRecord
from infrastructure.exceptions import VersionConflictError


class EventStore:

    def __init__(self, session: AsyncSession):
        self._session = session

    async def load(self, aggregate_id):
        stmt = (
            select(EventRecord)
            .where(EventRecord.aggregate_id == aggregate_id)
            .order_by(EventRecord.aggregate_version)
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def append(
        self,
        *,
        aggregate_id,
        aggregate_type,
        events,
        expected_version,
        metadata,
    ):
        current_version = await self._get_current_version(aggregate_id)

        if current_version != expected_version:
            raise VersionConflictError(
                aggregate_id=aggregate_id,
                expected=expected_version,
                actual=current_version,
            )

        next_version = current_version

        records = []

        for event in events:
            next_version += 1

            record = EventRecord(
                aggregate_id=aggregate_id,
                aggregate_type=aggregate_type,
                aggregate_version=next_version,
                event_type=event.__class__.__name__,
                payload=event.__dict__,
                metadata=metadata,
            )

            records.append(record)
            self._session.add(record)

        try:
            await self._session.flush()
        except IntegrityError:
            raise VersionConflictError(
                aggregate_id=aggregate_id,
                expected=expected_version,
                actual=current_version,
            )

        return records

    async def _get_current_version(self, aggregate_id):
        stmt = (
            select(EventRecord.aggregate_version)
            .where(EventRecord.aggregate_id == aggregate_id)
            .order_by(EventRecord.aggregate_version.desc())
            .limit(1)
        )
        result = await self._session.execute(stmt)
        row = result.scalar()
        return row or 0