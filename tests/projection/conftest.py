import pytest_asyncio

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)

from infrastructure.db.models import Base


DATABASE_URL = "postgresql+asyncpg://test:test@localhost:5433/basenode_test"


# engine должен быть function-scope
@pytest_asyncio.fixture(scope="function")
async def async_engine():

    engine = create_async_engine(
        DATABASE_URL,
        echo=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def async_session_factory(async_engine):

    return async_sessionmaker(
        bind=async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )