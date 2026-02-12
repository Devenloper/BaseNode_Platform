from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from infrastructure.db.repository import SqlAlchemyRepository


class SqlAlchemyUnitOfWork:

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self._session_factory = session_factory
        self._session: AsyncSession | None = None
        self.repository: SqlAlchemyRepository | None = None

    async def __aenter__(self):
        self._session = self._session_factory()

        # ВАЖНО: repository создаётся здесь,
        # чтобы использовать ту же session
        self.repository = SqlAlchemyRepository(self._session)

        return self

    async def __aexit__(self, exc_type, exc, tb):
        if exc:
            await self._session.rollback()
        else:
            await self._session.commit()

        await self._session.close()