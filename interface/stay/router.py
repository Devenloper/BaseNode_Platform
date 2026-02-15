from uuid import uuid4

from fastapi import APIRouter, Depends, status

from interface.stay.schemas import CheckInRequest
from interface.dependencies import get_check_in_handler

from application.stay.check_in import CheckInStay


router = APIRouter(
    prefix="/stays",
    tags=["stays"],
)


@router.post(
    "/check-in",
    status_code=status.HTTP_201_CREATED,
)
async def check_in_stay(
    request: CheckInRequest,
    handler=Depends(get_check_in_handler),
):
    command = CheckInStay(
        stay_id=request.stay_id,
        room_id=request.room_id,
        started_at=request.started_at,
        expected_version=request.expected_version,
        correlation_id=uuid4(),
        causation_id=uuid4(),
    )

    await handler.handle(command)

    return {"status": "ok"}