import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from datetime import datetime, timezone

from application.handlers.stay_handlers import CheckInStayHandler
from application.commands.stay_commands import CheckInStay
from application.exceptions import InvalidExpectedVersionError
from domain.stay.aggregate import Stay


def now():
    return datetime.now(timezone.utc)


def make_command(expected_version=0):
    return CheckInStay(
        stay_id=uuid4(),
        room_id="101",
        started_at=now(),
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
async def test_expected_version_is_passed_to_save():
    stay = Stay(uuid4())
    command = make_command(expected_version=5)

    uow = make_uow_with_stay(stay)
    handler = CheckInStayHandler(lambda: uow)

    await handler.handle(command)

    _, kwargs = uow.repository.save.await_args
    assert kwargs["expected_version"] == 5


@pytest.mark.asyncio
async def test_save_is_called_once():
    stay = Stay(uuid4())
    command = make_command(expected_version=0)

    uow = make_uow_with_stay(stay)
    handler = CheckInStayHandler(lambda: uow)

    await handler.handle(command)

    uow.repository.save.assert_awaited_once()


@pytest.mark.asyncio
async def test_domain_check_in_is_called():
    stay = Stay(uuid4())
    command = make_command()

    uow = make_uow_with_stay(stay)
    handler = CheckInStayHandler(lambda: uow)

    await handler.handle(command)

    assert stay.room_id == "101"


@pytest.mark.asyncio
async def test_invalid_expected_version_raises_error():
    stay = Stay(uuid4())
    command = make_command(expected_version=-1)

    uow = make_uow_with_stay(stay)
    handler = CheckInStayHandler(lambda: uow)

    with pytest.raises(InvalidExpectedVersionError):
        await handler.handle(command)