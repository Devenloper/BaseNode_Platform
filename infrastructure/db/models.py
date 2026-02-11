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
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import expression

Base = declarative_base()


class EventRecord(Base):
    __tablename__ = "event_store"

    id = Column(BigInteger, primary_key=True)  # global ordering

    aggregate_id = Column(UUID(as_uuid=True), nullable=False)
    aggregate_type = Column(String, nullable=False)

    aggregate_version = Column(Integer, nullable=False)

    event_type = Column(String, nullable=False)
    payload = Column(JSON, nullable=False)
    metadata = Column(JSON, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint(
            "aggregate_id",
            "aggregate_version",
            name="uq_aggregate_version",
        ),
        Index("ix_aggregate_id", "aggregate_id"),
    )


class OutboxRecord(Base):
    __tablename__ = "outbox"

    id = Column(BigInteger, primary_key=True)

    event_id = Column(BigInteger, nullable=False, unique=True)

    aggregate_id = Column(UUID(as_uuid=True), nullable=False)
    event_type = Column(String, nullable=False)

    payload = Column(JSON, nullable=False)

    correlation_id = Column(UUID(as_uuid=True), nullable=True)

    published = Column(
        expression.Boolean(),
        nullable=False,
        default=False,
        server_default=expression.false(),
    )

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("ix_outbox_published", "published"),
    )