# PROJECT_STATE.md

## 1. Project Status Snapshot

Project: **BaseNode Platform (Backend Core)**  
Architecture: DDD + Event Sourcing + Transactional Outbox  
Stage: Core backend skeleton stabilized

This document фиксирует текущее состояние реализации
и служит checkpoint-документом для передачи контекста
новому архитектору или координатору.

---

## 2. Implemented Layers

### ✅ Domain Layer — Stable

Implemented:

- Stay aggregate (ADR-0006 compliant)
- BaseAggregate abstraction (ADR-0007 compliant)
- Domain Events (pure, no metadata)
- Strict state machine
- Deterministic replay
- Handler table pattern
- Version semantics enforced

Test coverage:  
Domain ~93–100%

Guarantees:

- No I/O
- No infrastructure dependencies
- Version increments only in apply()
- Lifecycle changes only via events

Status: **Stable**

---

### ✅ Application Layer — Stable Skeleton

Implemented:

- Commands (explicit expected_version)
- Handlers (one handler = one transaction)
- UnitOfWork abstraction
- AggregateRepository abstraction
- No commit outside UoW
- No FastAPI imports
- No SQLAlchemy imports

Handlers perform:
async with uow:
load
domain operation
save
Test coverage:  
Application ~75–100%

Status: **Stable skeleton**

---

### ⚠ Infrastructure Layer — Implemented, Under Audit

Implemented components:

- EventStore (append-only)
- Repository
- UnitOfWork (commit in __aexit__)
- OutboxStore
- SQLAlchemy models

Validated:

- No UPDATE / DELETE
- Optimistic locking implemented
- Unique constraint on (aggregate_id, aggregate_version)
- VersionConflictError handled

⚠ Critical note:

Transactional Outbox integration must be verified to ensure:

- Outbox append occurs in same transaction
- EventStore + Outbox atomicity guaranteed

Status: **Functional, requires atomicity verification**

---

### ⏳ Interface Layer — Not Yet Implemented

Planned:

- FastAPI
- Router per aggregate
- DTO → Command mapping
- DI wiring Infrastructure → Application

No HTTP layer currently exists.

---

## 3. Test Status

Current test state:

- Domain tests passing
- Application tests passing
- BaseAggregate tests passing
- Coverage approx. 94%

Remaining:

- Infrastructure integration tests
- Outbox atomicity tests
- End-to-end flow tests
- Interface tests (future)

---

## 4. Architecture Enforcement

Active protections:

- architecture-gate.py
- Repository structure lock (ADR-0005)
- Boundary import validation (ADR-0002)
- Core Frozen rules (ADR-0001)

CI blocks merge on violations.

---

## 5. Current Development Focus

Next architectural step options:

Option A — Complete Infrastructure Hardening
- Ensure Outbox atomicity
- Add integration tests
- Validate deterministic serialization

Option B — Implement Interface Layer (FastAPI)
- Create interface/
- Wire DI
- Add HTTP endpoints
- Add contract tests

Recommended next step:
👉 Finalize Infrastructure atomic guarantees before exposing HTTP.

---

## 6. Known Risks

- Replay determinism depends on strict serialization
- Datetime timezone consistency must be enforced
- Outbox must be verified as truly transactional

---

## 7. Source of Truth

Architecture defined by:

- ARCHITECTURE.md
- ARCHITECTURE_CONTEXT.md
- docs/adr/*
- architecture-gate.py

This document reflects implementation state,
not architectural decisions.

---

## 8. Handover Summary

At this checkpoint:

- Core Domain is stable
- Application skeleton is stable
- Infrastructure is implemented but must be hardened
- Interface layer not yet started

System is safe for continuation,
but not yet ready for production traffic.

---

Checkpoint created to enable safe transfer to new coordinator.