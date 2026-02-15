# application/stay/relocate.py

from uuid import UUID
from datetime import datetime

from domain.stay.aggregate import Stay


class RelocateHandler:

    def __init__(self, uow_factory):
        self._uow_factory = uow_factory


    async def handle(
        self,
        stay_id: UUID,
        new_room_id: str,
        relocated_at: datetime,
    ) -> None:

        async with self._uow_factory() as uow:

            stay = await uow.repository.load(Stay, stay_id)

            if stay is None:
                raise ValueError("Stay not found")

            stay.relocate(
                new_room_id=new_room_id,
                relocated_at=relocated_at,
            )

            await uow.repository.save(
                stay,
                expected_version=stay.version - 1,
                metadata={},
            )