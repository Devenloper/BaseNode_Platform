# event_store/repository.py

from typing import List
from sqlalchemy import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from .model import EventStoreModel
from .base_event import BaseEvent
from .exceptions import (
    ConcurrencyConflict,
    IdempotencyConflict,
    DuplicateEventId,
)


class EventRepository:

    def __init__(self, session: AsyncSession):
        self._session = session

    # =========================================================
    # APPEND (STRICT ARCHITECTURE)
    # =========================================================
    async def append(self, events: List[BaseEvent]) -> None:

        if not events:
            return

        # -----------------------------------------------------
        # 1. Must run inside existing transaction
        # -----------------------------------------------------
        if not self._session.in_transaction():
            raise RuntimeError("append() must be executed inside active transaction")

        # -----------------------------------------------------
        # 2. Boundary validation (infrastructure-level)
        # -----------------------------------------------------
        first = events[0]
        tenant_id = first.tenant_id
        aggregate_id = first.aggregate_id

        expected_version = first.version

        for event in events:
            if event.tenant_id != tenant_id:
                raise ValueError("Batch contains multiple tenant_id")

            if event.aggregate_id != aggregate_id:
                raise ValueError("Batch contains multiple aggregate_id")

            if event.version != expected_version:
                raise ValueError("Batch versions must be sequential without gaps")

            expected_version += 1

        # -----------------------------------------------------
        # 3. Prepare insert rows (no mutation)
        # -----------------------------------------------------
        rows = [
            {
                "event_id": e.event_id,
                "aggregate_id": e.aggregate_id,
                "aggregate_type": e.aggregate_type,
                "event_type": e.event_type,
                "version": e.version,
                "payload": e.payload,
                "timestamp": e.timestamp,
                "actor": e.actor,
                "correlation_id": e.correlation_id,
                "causation_id": e.causation_id,
                "external_event_id": e.external_event_id,
                "tenant_id": e.tenant_id,
            }
            for e in events
        ]

        stmt = insert(EventStoreModel).values(rows)

        # -----------------------------------------------------
        # 4. Execute (constraint-driven)
        # -----------------------------------------------------
        try:
            await self._session.execute(stmt)

        except IntegrityError as exc:

            # Do NOT commit
            # Do NOT retry
            # Do NOT SELECT-before-INSERT

            constraint_name = getattr(exc.orig, "diag", None)
            constraint_name = getattr(constraint_name, "constraint_name", "")

            if constraint_name == "uq_event_store_aggregate_version":
                raise ConcurrencyConflict() from exc

            if constraint_name == "uq_event_store_external_event_id":
                raise IdempotencyConflict() from exc

            if constraint_name == "uq_event_store_event_id":
                raise DuplicateEventId() from exc

            raise