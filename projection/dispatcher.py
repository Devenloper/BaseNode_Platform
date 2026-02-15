# projection/dispatcher.py

import logging
from datetime import datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

# FIX: correct import location
from infrastructure.db.models import OutboxRecord

from domain.stay.events import (
    StayCheckedIn,
    StayCheckedOut,
)

from projection.projector import Projector
from projection.repository import StayProjectionRepository


logger = logging.getLogger(__name__)

class ProjectionDispatcher:

    def __init__(
        self,
        session: AsyncSession,
    ):

        self._session = session

        self._repository = StayProjectionRepository(
            session
        )

        self._projector = Projector(
            self._repository
        )

    async def dispatch(
        self,
        record: OutboxRecord,
    ) -> None:

        event = self._rebuild_event(record)

        await self._projector.project(event)

    @staticmethod
    def _rebuild_event(
        record: OutboxRecord,
    ):

        payload = record.payload

        if record.event_type == "StayCheckedIn":

            event = StayCheckedIn(
                stay_id=UUID(payload["stay_id"]),
                room_id=payload["room_id"],
                started_at=datetime.fromisoformat(
                    payload["started_at"]
                ),
            )

        elif record.event_type == "StayCheckedOut":

            event = StayCheckedOut(
                stay_id=UUID(payload["stay_id"]),
                ended_at=datetime.fromisoformat(
                    payload["ended_at"]
                ),
            )

        else:

            raise RuntimeError(
                f"Unknown event type {record.event_type}"
            )

        # inject version metadata
        object.__setattr__(
            event,
            "version",
            record.aggregate_version,
        )

        return event