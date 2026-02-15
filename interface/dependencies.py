# interface/dependencies.py

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from interface.config import get_settings

from infrastructure.db.unit_of_work import SqlAlchemyUnitOfWork

# application handlers
from application.stay.check_in import CheckInHandler
from application.stay.check_out import CheckOutHandler
from application.stay.relocate import RelocateHandler


settings = get_settings()


# =========================================================
# Engine — singleton
# =========================================================

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DB_ECHO,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
)


# =========================================================
# Session factory — singleton
# =========================================================

session_factory = async_sessionmaker(
    engine,
    expire_on_commit=False,
)


# =========================================================
# UnitOfWork factory
# =========================================================

def get_uow_factory():
    """
    Returns UoW factory.

    UoW is created per request.
    Engine and session factory remain singleton.
    """

    def factory():
        return SqlAlchemyUnitOfWork(session_factory)

    return factory


# =========================================================
# Handlers factories
# =========================================================

def get_check_in_handler() -> CheckInHandler:
    """
    Dependency for CheckIn HTTP endpoint.
    """
    return CheckInHandler(get_uow_factory())


def get_check_out_handler() -> CheckOutHandler:
    """
    Dependency for CheckOut HTTP endpoint.
    """
    return CheckOutHandler(get_uow_factory())


def get_relocate_handler() -> RelocateHandler:
    """
    Dependency for Relocate HTTP endpoint.
    """
    return RelocateHandler(get_uow_factory())