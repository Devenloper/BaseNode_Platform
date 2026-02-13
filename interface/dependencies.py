# interface/dependencies.py

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from interface.config import get_settings
from infrastructure.db.unit_of_work import SqlAlchemyUnitOfWork


settings = get_settings()


# ---------------------------------------------------------
# Engine — singleton (process-level)
# ---------------------------------------------------------

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DB_ECHO,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
)


# ---------------------------------------------------------
# Session factory — singleton
# ---------------------------------------------------------

session_factory = async_sessionmaker(
    engine,
    expire_on_commit=False,
)


# ---------------------------------------------------------
# UoW factory — per request
# ---------------------------------------------------------

def get_uow_factory():
    """
    Returns UnitOfWork factory.

    UoW is created per handler invocation.
    Engine is NOT recreated.
    """

    def factory():
        return SqlAlchemyUnitOfWork(session_factory)

    return factory