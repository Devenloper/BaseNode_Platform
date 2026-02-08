from datetime import datetime
from uuid import UUID as PyUUID

from sqlalchemy import (
    BigInteger,
    Integer,
    String,
    Text,
    TIMESTAMP,
    CheckConstraint,
    UniqueConstraint,
    Index,
    text,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


# ============================================================
# Base declarative class
# ============================================================

class Base(DeclarativeBase):
    pass


# ============================================================
# Event Store (Append-Only)
# ============================================================

class EventStoreModel(Base):
    __tablename__ = "event_store"

    # =========================================================
    # Global order (append-only, strict monotonic sequence)
    # =========================================================
    sequence_id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,  # GENERATED ALWAYS AS IDENTITY
    )

    # =========================================================
    # Core identifiers
    # =========================================================
    event_id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    aggregate_id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    aggregate_type: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    event_type: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    # =========================================================
    # Optimistic locking (aggregate version)
    # =========================================================
    version: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    # =========================================================
    # Immutable domain payload (JSONB)
    # =========================================================
    payload: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
    )

    # =========================================================
    # Metadata (must be provided by Command layer)
    # =========================================================
    timestamp: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,  # NO DEFAULT
    )

    actor: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    correlation_id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    causation_id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    # =========================================================
    # Idempotency (external integrations)
    # =========================================================
    external_event_id: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # =========================================================
    # Tenant isolation (shared table strategy)
    # =========================================================
    tenant_id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    # =========================================================
    # Constraints & Indexes
    # =========================================================
    __table_args__ = (

        # Event uniqueness within tenant
        UniqueConstraint(
            "tenant_id",
            "event_id",
            name="uq_event_store_event_id",
        ),

        # Optimistic concurrency control
        UniqueConstraint(
            "tenant_id",
            "aggregate_id",
            "version",
            name="uq_event_store_aggregate_version",
        ),

        # Version must be positive
        CheckConstraint(
            "version > 0",
            name="ck_event_store_version_positive",
        ),

        # Idempotency (partial unique index)
        Index(
            "uq_event_store_external_event_id",
            "tenant_id",
            "external_event_id",
            unique=True,
            postgresql_where=text("external_event_id IS NOT NULL"),
        ),

        # Fast aggregate replay
        Index(
            "ix_event_store_aggregate_replay",
            "tenant_id",
            "aggregate_id",
            "sequence_id",
        ),

        # System-wide replay / streaming
        Index(
            "ix_event_store_tenant_sequence",
            "tenant_id",
            "sequence_id",
        ),

        # Optional analytical rebuild support
        Index(
            "ix_event_store_aggregate_type",
            "tenant_id",
            "aggregate_type",
            "sequence_id",
        ),
    )