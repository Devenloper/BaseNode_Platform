# infrastructure/db/models.py

from sqlalchemy import (
    String,
    DateTime,
    func,
    CheckConstraint,
    UniqueConstraint,
    Index,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
from datetime import datetime


# ---------------------------------------------------------
# BASE
# ---------------------------------------------------------

class Base(DeclarativeBase):
    pass


# ---------------------------------------------------------
# EVENT STORE (Append-only)
# ---------------------------------------------------------

class EventRecord(Base):
    __tablename__ = "event_store"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    aggregate_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )

    aggregate_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    aggregate_version: Mapped[int] = mapped_column(
        nullable=False,
    )

    event_type: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    payload: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
    )

    event_metadata: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    __table_args__ = (
        # 🔒 Optimistic locking invariant
        UniqueConstraint(
            "aggregate_id",
            "aggregate_version",
            name="uq_event_store_aggregate_version",
        ),

        # 🔎 Deterministic replay performance
        Index(
            "ix_event_store_aggregate_order",
            "aggregate_id",
            "aggregate_version",
        ),

        # 🛡 Extra safeguard
        CheckConstraint(
            "aggregate_version > 0",
            name="ck_event_store_version_positive",
        ),
    )


# ---------------------------------------------------------
# OUTBOX (Transactional Outbox Pattern)
# ---------------------------------------------------------

class OutboxRecord(Base):
    __tablename__ = "outbox"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    aggregate_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )

    aggregate_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    aggregate_version: Mapped[int] = mapped_column(
        nullable=False,
    )

    event_type: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    payload: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
    )

    event_metadata: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
    )

    correlation_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    processed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    __table_args__ = (
        # Быстрый выбор непросессенных сообщений
        Index(
            "ix_outbox_unprocessed",
            "processed_at",
        ),
    )