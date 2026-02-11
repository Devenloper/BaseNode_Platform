import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from datetime import datetime

from application.handlers.stay_handlers import CheckInStayHandler
from application.commands.stay_commands import CheckInStay
from application.exceptions import InvalidExpectedVersionError
from domain.stay.aggregate import Stay


# ============================================================
# Test helpers
# ============================================================

def make_command(expected_version: int = 0):
    return CheckInStay(
        stay_id=uuid4(),
        room_id=uuid4(),
        started_at=datetime.utcnow(),
        expected_version=expected_version,
        actor="tester",
        correlation_id=uuid4(),
        causation_id=uuid4(),
    )


# ============================================================
# Mock UoW factory
# ============================================================

def make_uow_with_stay(stay: Stay):
    uow = MagicMock()
    uow.__aenter__ = AsyncMock(return_value=uow)
    uow.__aexit__ = AsyncMock(return_value=None)

    uow.repository = MagicMock()
    uow.repository.load = AsyncMock(return_value=stay)
    uow.repository.save = AsyncMock()

    return uow


# ============================================================
# Tests
# ============================================================

@pytest.mark.asyncio
async def test_expected_version_is_passed_to_save():
    stay = Stay(uuid4())
    command = make_command(expected_version=5)

    uow = make_uow_with_stay(stay)
    handler = CheckInStayHandler(lambda: uow)

    await handler.handle(command)

    uow.repository.save.assert_awaited_once()

    _, kwargs = uow.repository.save.call_args
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
    stay.check_in = MagicMock()

    command = make_command(expected_version=0)

    uow = make_uow_with_stay(stay)
    handler = CheckInStayHandler(lambda: uow)

    await handler.handle(command)

    stay.check_in.assert_called_once_with(
        room_id=command.room_id,
        started_at=command.started_at,
    )


@pytest.mark.asyncio
async def test_invalid_expected_version_raises_error():
    stay = Stay(uuid4())
    command = make_command(expected_version=-1)

    uow = make_uow_with_stay(stay)
    handler = CheckInStayHandler(lambda: uow)

    with pytest.raises(InvalidExpectedVersionError):
        await handler.handle(command)

    uow.repository.load.assert_not_called()
    uow.repository.save.assert_not_called()