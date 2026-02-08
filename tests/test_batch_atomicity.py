# tests/test_batch_atomicity.py

import pytest
from uuid import uuid4
from datetime import datetime, timezone

from event_store.repository import EventRepository
from event_store.exceptions import ConcurrencyConflict
from event_store.base_event import BaseEvent


@pytest.mark.asyncio
async def test_batch_atomicity(session):

    repo = EventRepository(session)

    tenant_id = uuid4()
    aggregate_id = uuid4()

    # First insert version 1
    first = BaseEvent(
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

    await repo.append([first])

    # Batch where second event conflicts
    batch = [
        BaseEvent(
            event_id=uuid4(),
            aggregate_id=aggregate_id,
            aggregate_type="Test",
            event_type="Updated",
            version=2,
            timestamp=datetime.now(timezone.utc),
            actor="tester",
            correlation_id=uuid4(),
            causation_id=uuid4(),
            external_event_id=None,
            tenant_id=tenant_id,
            payload={"x": 2},
        ),
        BaseEvent(
            event_id=uuid4(),
            aggregate_id=aggregate_id,
            aggregate_type="Test",
            event_type="Broken",
            version=1,  # violates unique (tenant, aggregate, version)
            timestamp=datetime.now(timezone.utc),
            actor="tester",
            correlation_id=uuid4(),
            causation_id=uuid4(),
            external_event_id=None,
            tenant_id=tenant_id,
            payload={"x": 3},
        ),
    ]

    with pytest.raises(ValueError):
        await repo.append(batch)

    # Ensure only original event exists
    loaded = await repo.load_aggregate(tenant_id, aggregate_id)
    assert len(loaded) == 1