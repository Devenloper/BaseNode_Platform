import pytest
from uuid import uuid4
from datetime import datetime, timezone

from domain.stay.aggregate import Stay


@pytest.mark.asyncio
async def test_uncommitted_events_cleared(uow):
    stay_id = uuid4()

    async with uow:
        stay = Stay(stay_id)

        stay.check_in(
            room_id="101",
            started_at=datetime.now(timezone.utc),
        )

        assert len(stay.get_uncommitted_events()) == 1

        await uow.repository.save(
            stay,
            expected_version=0,
            metadata={},
        )

        # после save uncommitted должны быть очищены
        assert len(stay.get_uncommitted_events()) == 0