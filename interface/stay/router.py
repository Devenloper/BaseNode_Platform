# interface/stay/router.py

from fastapi import APIRouter, Depends, status
from uuid import uuid4

from interface.stay.schemas import (
    CheckInStayRequest,
    CheckInStayResponse,
)
from interface.dependencies import get_check_in_handler

from application.commands.stay_commands import CheckInStay


router = APIRouter(
    prefix="/stays",
    tags=["stays"],
)


@router.post(
    "/check-in",
    response_model=CheckInStayResponse,
    status_code=status.HTTP_201_CREATED,
)
async def check_in_stay(
    request: CheckInStayRequest,
    handler=Depends(get_check_in_handler),
):
    """
    Thin HTTP endpoint.

    Flow:
    DTO → Command → Handler
    """

    command = CheckInStay(
        stay_id=request.stay_id,
        room_id=request.room_id,
        started_at=request.started_at,
        expected_version=request.expected_version,
        actor="system",  # временно до внедрения Auth
        correlation_id=uuid4(),
        causation_id=uuid4(),
    )

    await handler.handle(command)

    return CheckInStayResponse(status="accepted")