import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from datetime import datetime

from application.handlers.stay_handlers import RelocateStayHandler
from application.commands.stay_commands import RelocateStay
from domain.stay.aggregate import Stay


def make_command(expected_version=0):
    return RelocateStay(
        stay_id=uuid4(),
        new_room_id=uuid4(),
        relocated_at=datetime.utcnow(),
        expected_version=expected_version,
        actor="tester",
        correlation_id=uuid4(),
        causation_id=uuid4(),
    )


def make_uow_with_stay(stay):
    uow = MagicMock()
    uow.__aenter__ = AsyncMock(return_value=uow)
    uow.__aexit__ = AsyncMock(return_value=None)

    uow.repository = MagicMock()
    uow.repository.load = AsyncMock(return_value=stay)
    uow.repository.save = AsyncMock()

    return uow


@pytest.mark.asyncio
async def test_relocate_handler_calls_domain_and_save():
    stay = Stay(uuid4())
    stay.check_in(uuid4(), datetime.utcnow())

    command = make_command(expected_version=1)

    uow = make_uow_with_stay(stay)
    handler = RelocateStayHandler(lambda: uow)

    await handler.handle(command)

    uow.repository.save.assert_awaited_once()


@pytest.mark.asyncio
async def test_version_conflict_propagates_from_relocate():
    stay = Stay(uuid4())
    stay.check_in(uuid4(), datetime.utcnow())

    command = make_command(expected_version=1)

    uow = make_uow_with_stay(stay)
    uow.repository.save = AsyncMock(side_effect=RuntimeError("Version conflict"))

    handler = RelocateStayHandler(lambda: uow)

    with pytest.raises(RuntimeError):
        await handler.handle(command)