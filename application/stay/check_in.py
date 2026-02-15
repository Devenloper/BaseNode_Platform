from dataclasses import dataclass
from uuid import UUID, uuid4
from datetime import datetime

from domain.stay.aggregate import Stay
from domain.common.base_aggregate import DomainError


# COMMAND

@dataclass(frozen=True)
class CheckInStay:
    stay_id: UUID
    room_id: str
    started_at: datetime
    expected_version: int

    correlation_id: UUID
    causation_id: UUID


# HANDLER

class CheckInHandler:

    def __init__(self, repository, uow):
        self.repository = repository
        self.uow = uow

    async def handle(self, command: CheckInStay) -> None:

        async with self.uow:

            stay = await self.repository.load(Stay, command.stay_id)

            if stay is None:
                stay = Stay(command.stay_id)

            stay.check_in(
                room_id=command.room_id,
                started_at=command.started_at,
            )

            await self.repository.save(
                stay,
                expected_version=command.expected_version,
                metadata={
                    "correlation_id": str(command.correlation_id),
                    "causation_id": str(command.causation_id),
                },
            )