# projection/repository.py

from infrastructure.db.models import StayReadModel


class StayProjectionRepository:

    def __init__(self, session):
        self.session = session


    async def get(self, stay_id):

        return await self.session.get(
            StayReadModel,
            stay_id,
        )


    async def save(self, model):

        self.session.add(model)
        await self.session.flush()


    async def upsert(self, model):

        existing = await self.get(model.stay_id)

        if existing is None:

            await self.save(model)
            return

        if model.version <= existing.version:
            return

        existing.room_id = model.room_id
        existing.status = model.status
        existing.started_at = model.started_at
        existing.version = model.version

        await self.session.flush()