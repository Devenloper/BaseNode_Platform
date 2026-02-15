import pytest
from uuid import uuid4
from datetime import datetime, timezone

from projection.repository import StayProjectionRepository
from projection.models import StayReadModel


@pytest.mark.asyncio
async def test_repository_insert(async_session_factory):

    stay_id = uuid4()

    async with async_session_factory() as session:

        repo = StayProjectionRepository(session)

        model = StayReadModel(
            stay_id=stay_id,
            room_id="101",
            status="CHECKED_IN",
            started_at=datetime.now(timezone.utc),
            version=1,
        )

        await repo.upsert(model)

        await session.commit()

    async with async_session_factory() as session:

        loaded = await session.get(StayReadModel, stay_id)

        assert loaded is not None
        assert loaded.version == 1


@pytest.mark.asyncio
async def test_repository_update(async_session_factory):

    stay_id = uuid4()

    async with async_session_factory() as session:

        repo = StayProjectionRepository(session)

        model1 = StayReadModel(
            stay_id=stay_id,
            room_id="101",
            status="CHECKED_IN",
            started_at=datetime.now(timezone.utc),
            version=1,
        )

        await repo.upsert(model1)

        model2 = StayReadModel(
            stay_id=stay_id,
            room_id="202",
            status="CHECKED_IN",
            started_at=model1.started_at,
            version=2,
        )

        await repo.upsert(model2)

        await session.commit()

    async with async_session_factory() as session:

        loaded = await session.get(StayReadModel, stay_id)

        assert loaded.room_id == "202"
        assert loaded.version == 2


@pytest.mark.asyncio
async def test_repository_idempotent(async_session_factory):

    stay_id = uuid4()

    async with async_session_factory() as session:

        repo = StayProjectionRepository(session)

        model = StayReadModel(
            stay_id=stay_id,
            room_id="101",
            status="CHECKED_IN",
            started_at=datetime.now(timezone.utc),
            version=1,
        )

        await repo.upsert(model)
        await repo.upsert(model)

        await session.commit()

    async with async_session_factory() as session:

        loaded = await session.get(StayReadModel, stay_id)

        assert loaded.version == 1