import pytest
from uuid import uuid4
from datetime import datetime, timezone

from sqlalchemy import select

from infrastructure.db.models import OutboxRecord
from infrastructure.outbox.dispatcher import OutboxDispatcher
from projection.projector import Projector
from projection.models import StayReadModel


@pytest.mark.asyncio
async def test_dispatcher_process(async_session_factory):

    stay_id = uuid4()

    async with async_session_factory() as session:

        outbox = OutboxRecord(
            aggregate_id=stay_id,
            aggregate_type="Stay",
            aggregate_version=1,
            event_type="StayCheckedIn",
            payload={
                "stay_id": str(stay_id),
                "room_id": "101",
                "started_at": datetime.now(timezone.utc).isoformat(),
                "version": 1,
            },
            event_metadata={},
        )

        session.add(outbox)

        await session.commit()

    dispatcher = OutboxDispatcher(
        session_factory=async_session_factory,
        projector=Projector(),
    )

    processed = await dispatcher.dispatch_batch()

    assert processed == 1

    async with async_session_factory() as session:

        result = await session.execute(
            select(OutboxRecord)
        )

        record = result.scalar_one()

        assert record.published_at is not None

        projection = await session.get(
            StayReadModel,
            stay_id,
        )

        assert projection is not None


@pytest.mark.asyncio
async def test_dispatcher_idempotent(async_session_factory):

    stay_id = uuid4()

    async with async_session_factory() as session:

        outbox = OutboxRecord(
            aggregate_id=stay_id,
            aggregate_type="Stay",
            aggregate_version=1,
            event_type="StayCheckedIn",
            payload={
                "stay_id": str(stay_id),
                "room_id": "101",
                "started_at": datetime.now(timezone.utc).isoformat(),
                "version": 1,
            },
            event_metadata={},
        )

        session.add(outbox)
        await session.commit()

    dispatcher = OutboxDispatcher(
        session_factory=async_session_factory,
        projector=Projector(),
    )

    await dispatcher.dispatch_batch()
    processed = await dispatcher.dispatch_batch()

    assert processed == 0