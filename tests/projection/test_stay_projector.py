import pytest

from datetime import datetime, timezone
from uuid import uuid4

from domain.stay.events import StayCheckedIn

from projection.projector import Projector
from projection.repository import StayProjectionRepository


@pytest.mark.asyncio
async def test_projection_checked_in(async_session_factory):

    stay_id = uuid4()

    event = StayCheckedIn(
        stay_id=stay_id,
        room_id="101",
        started_at=datetime.now(timezone.utc),
    )

    event.version = 1

    async with async_session_factory() as session:

        repo = StayProjectionRepository(session)

        projector = Projector()

        await projector.project(event, repo)

        await session.commit()

        result = await repo.get(stay_id)

        assert result is not None
        assert result.room_id == "101"
        assert result.version == 1