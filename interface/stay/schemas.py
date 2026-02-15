from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CheckInRequest(BaseModel):
    """
    HTTP request schema for Stay check-in.
    """

    stay_id: UUID
    room_id: str
    started_at: datetime
    expected_version: int = Field(ge=0)

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        json_schema_extra={
            "example": {
                "stay_id": "550e8400-e29b-41d4-a716-446655440000",
                "room_id": "101",
                "started_at": "2026-01-01T12:00:00Z",
                "expected_version": 0,
            }
        },
    )