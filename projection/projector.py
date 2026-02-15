from datetime import datetime
from typing import Any

from domain.stay.events import StayCheckedIn
from projection.models import StayReadModel
from projection.repository import StayProjectionRepository


class Projector:
    """
    Production-correct projector.

    Supports BOTH contracts:

    1. Dispatcher contract:
       project(session=..., event_type=..., payload=..., aggregate_version=...)

    2. Direct event contract (tests, replay):
       project(event, repo)
    """

    async def project(self, *args, **kwargs) -> None:

        # ---------------------------------------------------------
        # Contract 1 — Dispatcher style
        # ---------------------------------------------------------
        if "session" in kwargs:

            session = kwargs["session"]
            event_type = kwargs["event_type"]
            payload = kwargs["payload"]
            aggregate_version = kwargs["aggregate_version"]

            repo = StayProjectionRepository(session)

            if event_type == "StayCheckedIn":

                model = StayReadModel(
                    stay_id=payload["stay_id"],
                    room_id=payload["room_id"],
                    status="CHECKED_IN",
                    started_at=datetime.fromisoformat(payload["started_at"]),
                    version=aggregate_version,
                )

                await repo.upsert(model)

            return

        # ---------------------------------------------------------
        # Contract 2 — Direct event style (tests, replay)
        # ---------------------------------------------------------
        event = args[0]
        repo: StayProjectionRepository = args[1]

        if isinstance(event, StayCheckedIn):

            if event.version is None:
                raise RuntimeError(
                    "Event version must be injected before projection"
                )

            model = StayReadModel(
                stay_id=event.stay_id,
                room_id=event.room_id,
                status="CHECKED_IN",
                started_at=event.started_at,
                version=event.version,
            )

            await repo.upsert(model)