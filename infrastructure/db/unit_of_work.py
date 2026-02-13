# infrastructure/db/unit_of_work.py

from infrastructure.db.repository import SqlAlchemyRepository


class SqlAlchemyUnitOfWork:
    """
    UoW:
    - Commit только в __aexit__
    - Repository создаётся внутри контекста
    """

    def __init__(self, session_factory):
        self._session_factory = session_factory
        self._session = None
        self.repository = None

    async def __aenter__(self):
        self._session = self._session_factory()
        self.repository = SqlAlchemyRepository(self._session)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        try:
            if exc:
                await self._session.rollback()
            else:
                await self._session.commit()
        finally:
            await self._session.close()