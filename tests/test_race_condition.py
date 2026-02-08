# tests/test_race_condition.py

import asyncio
import pytest
from uuid import uuid4
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import async_sessionmaker
from event_store.repository import EventRepository
from event_store.exceptions import ConcurrencyConflict
from event_store.base_event import BaseEvent


@pytest.mark.asyncio
async def test_race_condition(engine):

    async_session = async_sessionmaker(engine, expire_on_commit=False)

    tenant_id = uuid4()
    aggregate_id = uuid4()

    async def writer():
        async with async_session() as session:
            async with session.begin():
                repo = EventRepository(session)

                event = BaseEvent(
                    event_id=uuid4(),
                    aggregate_id=aggregate_id,
                    aggregate_type="Test",
                    event_type="Created",
                    version=1,
                    timestamp=datetime.now(timezone.utc),
                    actor="tester",
                    correlation_id=uuid4(),
                    causation_id=uuid4(),
                    external_event_id=None,
                    tenant_id=tenant_id,
                    payload={"x": 1},
                )

                await repo.append([event])

    # Two concurrent writers
    results = await asyncio.gather(
        writer(),
        writer(),
        return_exceptions=True,
    )

    success_count = sum(1 for r in results if r is None)
    conflict_count = sum(1 for r in results if isinstance(r, ConcurrencyConflict))

    assert success_count == 1
    assert conflict_count == 1