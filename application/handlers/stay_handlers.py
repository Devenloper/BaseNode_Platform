from domain.stay.aggregate import Stay
from application.contracts.unit_of_work import UnitOfWork
from application.exceptions import InvalidExpectedVersionError
from application.commands.stay_commands import (
    CheckInStay,
    CheckOutStay,
    RelocateStay,
)


# ============================================================
# Base Handler Pattern
# ============================================================


class BaseStayHandler:
    def __init__(self, uow_factory):
        self._uow_factory = uow_factory


# ============================================================
# CheckIn Handler
# ============================================================


class CheckInStayHandler(BaseStayHandler):

    async def handle(self, command: CheckInStay) -> None:
        if command.expected_version < 0:
            raise InvalidExpectedVersionError()

        async with self._uow_factory() as uow:

            stay = await uow.repository.load(Stay, command.stay_id)

            stay.check_in(
                room_id=command.room_id,
                started_at=command.started_at,
            )

            await uow.repository.save(
                stay,
                expected_version=command.expected_version,
                metadata={
                    "actor": command.actor,
                    "correlation_id": command.correlation_id,
                    "causation_id": command.causation_id,
                    "source": "check_in_stay_handler",
                },
            )


# ============================================================
# CheckOut Handler
# ============================================================


class CheckOutStayHandler(BaseStayHandler):

    async def handle(self, command: CheckOutStay) -> None:
        if command.expected_version < 0:
            raise InvalidExpectedVersionError()

        async with self._uow_factory() as uow:

            stay = await uow.repository.load(Stay, command.stay_id)

            stay.check_out(
                ended_at=command.ended_at,
            )

            await uow.repository.save(
                stay,
                expected_version=command.expected_version,
                metadata={
                    "actor": command.actor,
                    "correlation_id": command.correlation_id,
                    "causation_id": command.causation_id,
                    "source": "check_out_stay_handler",
                },
            )


# ============================================================
# Relocate Handler
# ============================================================


class RelocateStayHandler(BaseStayHandler):

    async def handle(self, command: RelocateStay) -> None:
        if command.expected_version < 0:
            raise InvalidExpectedVersionError()

        async with self._uow_factory() as uow:

            stay = await uow.repository.load(Stay, command.stay_id)

            stay.relocate(
                new_room_id=command.new_room_id,
                relocated_at=command.relocated_at,
            )

            await uow.repository.save(
                stay,
                expected_version=command.expected_version,
                metadata={
                    "actor": command.actor,
                    "correlation_id": command.correlation_id,
                    "causation_id": command.causation_id,
                    "source": "relocate_stay_handler",
                },
            )