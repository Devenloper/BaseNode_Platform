# interface/stay/schemas.py

from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class CheckInStayRequest(BaseModel):
    """
    HTTP DTO.
    Не равен Domain Event.
    Не равен Application Command.
    """

    stay_id: UUID
    room_id: str
    started_at: datetime
    expected_version: int


class CheckInStayResponse(BaseModel):
    """
    HTTP response DTO.
    Не содержит бизнес-данных.
    """

    status: str