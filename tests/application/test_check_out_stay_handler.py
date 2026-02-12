import pytest
from uuid import uuid4
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

from application.handlers.stay_handlers import CheckOutStayHandler
from application.commands.stay_commands import CheckOutStay
from application.exceptions import InvalidExpectedVersionError
from domain.stay.aggregate import Stay


# -----------------------------------------------------------
# Helper
# -----------------------------------------------------------

def _build_handler(stay: Stay):
    uow = MagicMock()
    uow.__aenter__ = AsyncMock(return_value=uow)
    uow.__aexit__ = AsyncMock(return_value=None)

    uow.repository = MagicMock()
    uow.repository.load = AsyncMock(return_value=stay)
    uow.repository.save = AsyncMock(return_value=None)

    handler = CheckOutStayHandler(lambda: uow)
    return handler, uow


# -----------------------------------------------------------
# Tests
# -----------------------------------------------------------

@pytest.mark.asyncio
async def test_check_out_handler_calls_domain_and_save():
    stay_id = uuid4()
    now = datetime.now(timezone.utc)

    stay = Stay(stay_id)
    stay.check_in(room_id="101", started_at=now)

    handler, uow = _build_handler(stay)

    command = CheckOutStay(
        stay_id=stay_id,
        ended_at=now,
        expected_version=1,
        actor="tester",
        correlation_id=uuid4(),
        causation_id=uuid4(),
    )

    await handler.handle(command)

    uow.repository.load.assert_awaited_once()
    uow.repository.save.assert_awaited_once()


@pytest.mark.asyncio
async def test_expected_version_is_passed_to_save():
    stay_id = uuid4()
    now = datetime.now(timezone.utc)

    stay = Stay(stay_id)
    stay.check_in(room_id="101", started_at=now)

    handler, uow = _build_handler(stay)

    command = CheckOutStay(
        stay_id=stay_id,
        ended_at=now,
        expected_version=1,
        actor="tester",
        correlation_id=uuid4(),
        causation_id=uuid4(),
    )

    await handler.handle(command)

    _, kwargs = uow.repository.save.await_args
    assert kwargs["expected_version"] == 1


@pytest.mark.asyncio
async def test_invalid_expected_version_raises_error():
    stay_id = uuid4()
    now = datetime.now(timezone.utc)

    stay = Stay(stay_id)
    stay.check_in(room_id="101", started_at=now)

    handler, _ = _build_handler(stay)

    command = CheckOutStay(
        stay_id=stay_id,
        ended_at=now,
        expected_version=-1,
        actor="tester",
        correlation_id=uuid4(),
        causation_id=uuid4(),
    )

    with pytest.raises(InvalidExpectedVersionError):
        await handler.handle(command)