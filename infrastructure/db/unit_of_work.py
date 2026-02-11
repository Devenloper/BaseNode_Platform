from sqlalchemy.ext.asyncio import async_sessionmaker

from infrastructure.db.repository import SqlAlchemyRepository
from infrastructure.db.outbox import OutboxStore


class SqlAlchemyUnitOfWork:

    def __init__(self, session_factory: async_sessionmaker):
        self._session_factory = session_factory

    async def __aenter__(self):
        self._session = self._session_factory()
        self.repository = SqlAlchemyRepository(self._session)
        self.outbox = OutboxStore(self._session)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if exc:
            await self._session.rollback()
        else:
            await self._session.commit()

        await self._session.close()