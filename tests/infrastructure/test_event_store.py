import pytest
from uuid import uuid4
from datetime import datetime, timezone

from domain.stay.aggregate import Stay


@pytest.mark.asyncio
async def test_event_store_append_and_replay(uow):
    stay_id = uuid4()
    started_at = datetime.now(timezone.utc)

    # WRITE
    async with uow:
        stay = Stay(stay_id)

        stay.check_in(
            room_id="101",
            started_at=started_at,
        )

        await uow.repository.save(
            stay,
            expected_version=0,
            metadata={},
        )

    # READ (replay)
    async with uow:
        loaded = await uow.repository.load(Stay, stay_id)

        assert loaded.id == stay_id
        assert loaded.room_id == "101"
        assert loaded.started_at == started_at
        assert loaded._is_active is True
        assert loaded.version == 1