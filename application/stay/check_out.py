# application/stay/check_out.py

from uuid import UUID
from datetime import datetime

from domain.stay.aggregate import Stay


class CheckOutHandler:

    def __init__(self, uow_factory):
        self._uow_factory = uow_factory


    async def handle(
        self,
        stay_id: UUID,
        ended_at: datetime,
    ) -> None:

        async with self._uow_factory() as uow:

            stay = await uow.repository.load(Stay, stay_id)

            if stay is None:
                raise ValueError("Stay not found")

            stay.check_out(ended_at)

            await uow.repository.save(
                stay,
                expected_version=stay.version - 1,
                metadata={},
            )