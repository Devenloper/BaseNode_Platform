# ARCHITECTURE_CONTEXT.md

## 1. Project Overview

Проект: **BaseNode Platform (Backend Core)**

Архитектурный стиль:

- Domain-Driven Design (DDD)
- Event Sourcing
- CQRS (write-first модель)
- Append-only Event Store
- Transactional Outbox
- Optimistic Locking
- Deterministic Replay
- Modular Monolith (Layered Architecture)

⚠ Этот репозиторий — backend core.

Frontend-приложения (kioskUI, AdminUI) находятся вне данного репозитория.

---

## 2. Architectural Principles (Non-Negotiable)

Архитектура зафиксирована через ADR и защищается CI (architecture-gate).

### ADR-0001 — Core Frozen v1

- Event Store — append-only
- Нет UPDATE / DELETE
- Version не хранится в Domain Events
- Commit только в UnitOfWork
- Outbox обязан быть транзакционно атомарным
- Application слой не содержит бизнес-инвариантов

### ADR-0002 — Boundary Contracts

- Domain не знает о Application / Infrastructure / HTTP
- Application не знает о FastAPI / SQLAlchemy
- Infrastructure не формирует HTTP
- Interface не содержит бизнес-логики
- DTO не пересекают слои

### ADR-0005 — Repository Structure Lock

Разрешённые root-директории:

- domain
- application
- infrastructure
- interface
- contracts
- docs
- scripts
- tests
- .github

Любое изменение структуры требует ADR.

### ADR-0006 — Stay Aggregate State Machine

Lifecycle Stay:

- NOT_STARTED
- IN_PROGRESS
- COMPLETED

Разрешённые переходы:

- check_in → IN_PROGRESS
- check_out → COMPLETED
- relocate → IN_PROGRESS

Конфликт не является lifecycle состоянием.

### ADR-0007 — Core Aggregate Pattern

Все агрегаты обязаны:

- использовать handler table
- изменять состояние только через apply()
- увеличивать version только через события
- поддерживать deterministic replay
- не содержать I/O
- не зависеть от инфраструктуры

---

## 3. Current Repository Structure (Snapshot)
BaseNode_Platform/
│
├── domain/
│ ├── init.py
│ ├── common/
│ │ ├── init.py
│ │ └── base_aggregate.py
│ │
│ └── stay/
│ ├── init.py
│ ├── aggregate.py
│ ├── events.py
│ └── errors.py
│
├── application/
│ ├── init.py
│ ├── contracts/
│ │ ├── unit_of_work.py
│ │ └── aggregate_repository.py
│ │
│ └── stay/
│ ├── init.py
│ ├── commands.py
│ └── handlers.py
│
├── infrastructure/
│ ├── event_store.py
│ ├── repository.py
│ ├── unit_of_work.py
│ ├── outbox.py
│ └── models.py
│
├── interface/ # пока не реализован
│
├── tests/
│ ├── domain/
│ ├── application/
│ └── infrastructure/ # планируется
│
├── docs/
│ └── adr/
│
├── scripts/
│ └── architecture-gate.py
│
├── ARCHITECTURE.md
├── ARCHITECTURE_CONTEXT.md
└── pyproject.toml

---

## 4. Current Implementation Status

### Domain Layer

✔ Реализован Stay Aggregate  
✔ Event Sourcing  
✔ Invariants зафиксированы  
✔ BaseAggregate введён  
✔ Replay детерминирован  
✔ Покрытие тестами высокое  

Статус: Стабилен

---

### Application Layer

✔ Commands  
✔ Handlers (1 handler = 1 transaction = 1 aggregate)  
✔ expected_version передаётся явно  
✔ Нет commit внутри handler  
✔ Нет инфраструктурных зависимостей  

Статус: Стабилен

---

### Infrastructure Layer

Реализовано:

- EventStore (append-only)
- Optimistic locking
- Repository
- UnitOfWork (commit только в __aexit__)
- Outbox (реализация присутствует)

Требуется:

- Проверить транзакционную атомарность Outbox
- Integration tests для инфраструктуры

Статус: Требует проверки

---

### Interface Layer

Не реализован.

Следующий логический этап после стабилизации инфраструктуры.

---

## 5. Testing Status

- Domain tests — зелёные
- Application tests — зелёные
- BaseAggregate tests — зелёные
- Coverage высокий (~94%)

Infrastructure integration tests — требуется добавить.

---

## 6. Enforcement

Архитектура защищена:

- architecture-gate.py
- Boundary checks
- Repository structure validation
- Pull Request checklist
- ADR compliance

CI failure = merge запрещён.

---

## 7. Determinism & Replay Guarantees

- version увеличивается только через apply()
- replay не имеет побочных эффектов
- Domain Events не содержат metadata
- Domain Events содержат только бизнес-данные

Replay должен быть полностью воспроизводимым.

---

## 8. Current Strategic Direction

Текущий этап:

1. Зафиксировать Infrastructure (integration tests)
2. Убедиться в атомарности Outbox
3. После этого — переход к Interface (FastAPI)
4. Только после Interface — интеграция с frontend

---

## 9. What This Repository Is NOT

- Это не full-stack проект
- Это не frontend
- Это не микросервисная система
- Это modular monolith backend core

---

## 10. Source of Truth

Источники архитектурной правды:

- ARCHITECTURE.md
- ARCHITECTURE_CONTEXT.md
- docs/adr/*
- architecture-gate.py

Если правило:

- не описано в ADR
- не отражено в architecture-gate
- не включено в checklist

→ оно не является частью архитектуры.

---

## Final Note

Этот документ предназначен для:

- передачи новому координатору
- передачи новому архитектору
- восстановления контекста после паузы
- предотвращения архитектурной деградации

Любая дальнейшая работа должна начинаться с изучения этого файла.