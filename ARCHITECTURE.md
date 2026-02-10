# Architecture Overview — BaseNode Platform

## Purpose

Этот документ является **точкой входа в архитектуру проекта BaseNode Platform**.

Он фиксирует:
- текущую архитектурную модель
- неизменяемые контракты (Core Frozen v1)
- правила изменения архитектуры
- обязательные механизмы enforcement

Любое изменение, противоречащее этому документу,  
считается **архитектурным нарушением**.

---

## Architectural Status

**Architecture status:** 🔒 Core Frozen v1 (ACTIVE)

Архитектура проекта зафиксирована и защищена
на уровне:

- ADR
- CI
- структуры репозитория
- процессов Pull Request

---

## High-Level Architecture

Проект построен на следующих принципах:

- Domain-Driven Design (DDD)
- Event Sourcing
- CQRS (write-first)
- Append-only Event Store
- Unit of Work
- Transactional Outbox
- Deterministic replay
- Optimistic locking

Архитектура разделена на **4 слоя**:
Interface → Application → Domain
↑
Infrastructure
---

## Core Frozen v1

Минимальное неизменяемое ядро архитектуры зафиксировано в:

📄 `docs/adr/0001-core-frozen-v1.md`

Core Frozen v1 включает:

- Event Store контракт (append-only)
- UnitOfWork контракт
- Outbox модель
- Snapshot policy
- Application orchestration rules
- Event naming conventions

❗ Изменение любого из этих пунктов **запрещено**
без нового ADR.

---

## Boundary Contracts

Границы между слоями являются **строгими и нормативными**.

📄 `docs/adr/0002-boundary-contracts.md`

Кратко:

- Domain не зависит ни от кого
- Application оркестрирует, но не содержит бизнес-логики
- Infrastructure реализует технические детали
- Interface содержит только HTTP и DTO
- DTO и Pydantic не пересекают Domain/Application
- Исключения проходят только вверх по слоям

Нарушение boundary = архитектурный дефект.

---

## Repository Structure

Структура репозитория является частью архитектуры.

📄 `docs/adr/0005-repository-structure-lock.md`

Разрешённая root-структура:
Запрещено:

- добавлять новые root-директории
- использовать `shared/`, `common/`, `utils/`
- создавать параллельные слои
- перемещать существующие слои

Изменение структуры требует ADR.

---

## Architecture Validation

Архитектура проверяется **не на словах**, а автоматически.

### Architecture Gate (CI)

В проекте настроен единый CI gate:

- проверка boundary импортов
- проверка структуры репозитория

📄 `scripts/architecture-gate.py`  
📄 `docs/adr/0004-ci-boundary-enforcement.md`

Любое нарушение:
- блокирует CI
- блокирует merge
- не может быть проигнорировано

---

## Pull Request Rules

### Main branch

- 🔒 direct push запрещён
- ✅ merge только через Pull Request
- ✅ CI status checks обязательны

### Каждый PR обязан:

- проходить Architecture Gate
- соблюдать Architecture Validation Checklist
- **не менять архитектуру без ADR**

📄 `docs/adr/0003-architecture-validation-checklist.md`

---

## Architecture Changes Policy

### Любое архитектурное изменение требует ADR

К архитектурным изменениям относятся:

- изменение Core Frozen v1
- изменение boundary правил
- изменение структуры репозитория
- ослабление CI enforcement
- добавление новых слоёв
- изменение контрактов Event Store / UoW / Outbox

Процесс:

1. Создать новый ADR в `docs/adr/`
2. Описать Context / Decision / Enforcement
3. Обновить checklist / CI при необходимости
4. Только после этого менять код

Изменение кода **без ADR** = нарушение архитектуры.

---

## Source of Truth

Единственные источники архитектурной правды:

- `ARCHITECTURE.md` (этот документ)
- `docs/adr/*.md`
- Architecture Gate (CI)

Если правило:
- не описано в ADR
- не проверяется CI
- не включено в checklist  

→ оно **не считается частью архитектуры**.

---

## Final Rule

> Архитектура защищается не доверием,  
> а дисциплиной, процессами и автоматикой.

Любое ослабление этих механизмов
требует явного архитектурного решения (ADR).