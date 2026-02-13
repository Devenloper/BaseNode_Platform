import pytest
from uuid import uuid4
from datetime import datetime, timezone

from domain.stay.aggregate import Stay
from application.exceptions import VersionConflictError


@pytest.mark.asyncio
async def test_version_conflict(uow):
    stay_id = uuid4()

    # Первая транзакция
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

    # Вторая транзакция с неверной версией
    async with uow:
        stay = await uow.repository.load(Stay, stay_id)

        stay.check_out(
            ended_at=datetime.now(timezone.utc),
        )

        with pytest.raises(VersionConflictError):
            await uow.repository.save(
                stay,
                expected_version=0,  # ❌ устаревшая версия
                metadata={},
            )