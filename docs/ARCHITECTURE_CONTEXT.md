# ARCHITECTURE_CONTEXT.md

## 1. System Overview

Проект: **BaseNode Platform**

Архитектурный стиль:

- Domain-Driven Design (DDD)
- Event Sourcing
- CQRS (write-first)
- Append-only Event Store
- Transactional Outbox
- Optimistic Locking
- Deterministic replay

Система проектируется **строго от write-модели**.
Read-модель и проекции не являются частью Core v1.

На текущий момент:
- Архитектурное ядро зафиксировано
- Архитектура защищена CI
- Реализация доменной логики только начинается

---

## 2. Architecture Constraints (Non-negotiable)

Следующие архитектурные решения **зафиксированы и не подлежат изменению без нового ADR**.

### Core Architecture

- **ADR-0001 — Core Frozen v1**
  - Event Store: append-only
  - UnitOfWork: одна транзакция → один агрегат
  - Outbox: атомарен, без publish
  - Snapshot: вторичный артефакт
  - Application не содержит бизнес-инвариантов

### Boundary Rules

- **ADR-0002 — Boundary Contracts**
  - Domain не знает о Infrastructure / Application / HTTP
  - Application не знает о HTTP / SQLAlchemy
  - Infrastructure не формирует HTTP
  - Interface не содержит бизнес-логики

### Repository Structure

- **ADR-0005 — Repository Structure Lock**
  - Разрешённые root-директории зафиксированы
  - Запрещены `shared/`, `common/`, `utils/`
  - Любое изменение структуры = архитектурное изменение

---

## 3. Domain Model Status

### Aggregates

На текущий момент формализован **один агрегат**:

#### Stay Aggregate

- **ADR-0006 — Stay Aggregate State Machine**
- Lifecycle строго зафиксирован:

  - NOT_STARTED
  - IN_PROGRESS
  - COMPLETED

- Разрешённые переходы:
  - check_in → IN_PROGRESS
  - check_out → COMPLETED
  - relocate → IN_PROGRESS

- Конфликт **не является состоянием**
- State machine является частью Core Domain

Других агрегатов пока **не существует**.

---

## 4. Enforcement Mechanisms

Архитектура защищается **автоматически**.

### CI

- Единый Architecture Gate:
  - проверка boundary импортов
  - проверка структуры репозитория

Файл:
- `scripts/architecture-gate.py`

CI failure = merge невозможен.

### GitHub Policies

- `main` защищён
- direct push запрещён
- merge только через Pull Request
- CI status checks обязательны

### Process

- Pull Request Checklist обязателен
- Любое архитектурное изменение требует ADR
- Код без ADR считается дефектным

---

## 5. Current Development Focus

Текущая задача проекта:

> **Реализация первого Domain Aggregate — Stay — строго по ADR-0006**

Ограничения:

- Только Domain слой
- Только Event Sourcing модель
- Без Infrastructure
- Без Application
- Без HTTP
- Без DTO
- Без metadata в Domain Events

Цель текущего этапа:

- Получить эталонный агрегат
- Зафиксировать стиль доменной модели
- Использовать его как шаблон для следующих агрегатов

---

## 6. Source of Truth

Единственные источники архитектурной правды:

- `ARCHITECTURE.md`
- `ARCHITECTURE_CONTEXT.md`
- `docs/adr/*.md`
- Architecture Gate (CI)

Если правило:
- не описано в ADR
- не проверяется CI
- не включено в checklist

→ оно **не считается частью архитектуры**.

---

## Final Note

Этот документ предназначен для:

- onboarding нового архитектора
- передачи контекста новому чату
- восстановления архитектурного контекста после паузы

Любая реализация должна начинаться **с этого файла**.