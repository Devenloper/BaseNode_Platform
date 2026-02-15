from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID


@dataclass
class ProjectionEvent:

    aggregate_id: UUID
    aggregate_version: int
    event_type: str
    payload: dict[str, Any]
    created_at: datetime