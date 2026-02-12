from sqlalchemy import (
    Column,
    String,
    Integer,
    DateTime,
    JSON,
    BigInteger,
    UniqueConstraint,
    Index,
    func,
    Boolean,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base


Base = declarative_base()


# ============================================================
# Event Store
# ============================================================

class EventRecord(Base):
    __tablename__ = "event_store"

    # глобальный порядок событий
    id = Column(BigInteger, primary_key=True)

    aggregate_id = Column(UUID(as_uuid=True), nullable=False)
    aggregate_type = Column(String, nullable=False)

    aggregate_version = Column(Integer, nullable=False)

    event_type = Column(String, nullable=False)

    payload = Column(JSON, nullable=False)

    # ⚠ нельзя называть "metadata" — зарезервировано в SQLAlchemy
    event_metadata = Column("metadata", JSON, nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    __table_args__ = (
        UniqueConstraint(
            "aggregate_id",
            "aggregate_version",
            name="uq_aggregate_version",
        ),
        Index("ix_event_store_aggregate_id", "aggregate_id"),
    )


# ============================================================
# Outbox
# ============================================================

class OutboxRecord(Base):
    __tablename__ = "outbox"

    id = Column(BigInteger, primary_key=True)

    # ссылка на event_store.id
    event_id = Column(BigInteger, nullable=False, unique=True)

    aggregate_id = Column(UUID(as_uuid=True), nullable=False)

    event_type = Column(String, nullable=False)

    payload = Column(JSON, nullable=False)

    correlation_id = Column(UUID(as_uuid=True), nullable=True)

    published = Column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("false"),
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    __table_args__ = (
        Index("ix_outbox_published", "published"),
    )