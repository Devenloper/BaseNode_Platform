from .models import OutboxRecord


class OutboxStore:

    def __init__(self, session):
        self._session = session

    async def append(self, event_records):
        for record in event_records:
            outbox = OutboxRecord(
                event_id=record.id,
                aggregate_id=record.aggregate_id,
                event_type=record.event_type,
                payload=record.payload,
                correlation_id=record.event_metadata.get("correlation_id"),
            )
            self._session.add(outbox)