import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from infrastructure.db.models import Base
from infrastructure.db.unit_of_work import SqlAlchemyUnitOfWork


@pytest_asyncio.fixture
async def engine():
    engine = create_async_engine(
        "postgresql+asyncpg://test:test@localhost:5433/basenode_test",
        future=True,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture
async def uow(engine):
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    return SqlAlchemyUnitOfWork(session_factory)