import pytest
from uuid import uuid4
from datetime import datetime, timezone
from sqlalchemy import select

from domain.stay.aggregate import Stay
from infrastructure.db.models import EventRecord, OutboxRecord


@pytest.mark.asyncio
async def test_atomicity_rollback(engine, uow):
    stay_id = uuid4()

    # Принудительный rollback
    try:
        async with uow:
            stay = Stay(stay_id)

            stay.check_in(
                room_id="101",
                started_at=datetime.now(timezone.utc),
            )

            await uow.repository.save(
                stay,
                expected_version=0,
                metadata={},
            )

            raise RuntimeError("force rollback")

    except RuntimeError:
        pass

    # Проверяем, что ничего не записалось
    async with engine.connect() as conn:
        events = (await conn.execute(select(EventRecord))).scalars().all()
        outbox = (await conn.execute(select(OutboxRecord))).scalars().all()

        assert len(events) == 0
        assert len(outbox) == 0