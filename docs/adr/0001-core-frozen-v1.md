# ADR-0001: Core Frozen v1

Status: Accepted  
Date: 2026-02-09  
Authors: Architecture Team  
Related ADRs: 0002-boundary-contracts.md, 0003-architecture-validation-checklist.md, 0004-ci-boundary-enforcement.md  
Supersedes: None  

---

## 1. Context

Проект реализует архитектуру на основе:

- DDD
- Event Sourcing
- CQRS (write-first)
- Append-only Event Store
- UnitOfWork + AggregateRepository
- Transactional Outbox
- Snapshot (вторичный артефакт)

На этапе стабилизации ядра возник риск архитектурной деградации:

- добавление «временных» commit
- публикация событий вне Outbox
- дублирование инвариантов в Application
- изменение контракта Event Store
- расширение Domain техническими деталями

Для предотвращения деградации необходимо зафиксировать
неизменяемую часть архитектуры.

---

## 2. Decision

Принято решение объявить **Core Frozen v1**.

Это означает, что следующие архитектурные контракты являются неизменяемыми:

### 2.1 Event Store

- Append-only
- Нет UPDATE
- Нет DELETE
- UNIQUE (aggregate_id, aggregate_version)
- VersionConflict через optimistic locking
- IntegrityError маппится в VersionConflictError

Контракт Event Store изменению не подлежит.

---

### 2.2 UnitOfWork

- Одна транзакция — один агрегат
- Commit только в `__aexit__`
- Нет ручного commit в handler
- Нет commit внутри Outbox
- Нет commit вне UoW

Контракт UnitOfWork изменению не подлежит.

---

### 2.3 Outbox

- Записывается в той же транзакции
- Не делает commit
- Не публикует события
- Публикация выполняется воркером
- Публикация идемпотентна

Outbox модель неизменяема.

---

### 2.4 Snapshot Policy

- Snapshot сохраняется после commit
- Snapshot — вторичный артефакт
- Ошибка snapshot не откатывает события
- Snapshot можно пересоздать

Snapshot не влияет на Event Store.

---

### 2.5 Application Rules

- Одна команда — один агрегат — одна транзакция
- expected_version обязателен
- handler не подавляет Domain exceptions
- handler не делает commit вручную
- handler не публикует события напрямую

Application orchestration фиксирована.

---

### 2.6 Event Naming Conventions

- События отражают факт
- Нет абстрактных событий (например, StatusChanged)
- Нет технических полей в Domain events
- Нет metadata в Domain events
- Нет aggregate_version в Domain events

Naming rules фиксированы.

---

## 3. Rationale

Freeze введён для:

- защиты архитектурной целостности
- предотвращения «локальных компромиссов»
- обеспечения детерминизма replay
- обеспечения корректного optimistic locking
- предотвращения side-effects в write-модели

Без Freeze:

- возрастает риск скрытых зависимостей
- появляются commit вне UoW
- Outbox теряет атомарность
- Domain загрязняется инфраструктурой
- нарушается Event Sourcing модель

Freeze фиксирует минимально достаточную архитектуру v1.

---

## 4. Consequences

### 4.1 Положительные последствия

- архитектура становится предсказуемой
- replay детерминирован
- конкурентность контролируема
- границы слоёв стабилизированы
- CI может enforce’ить правила

---

### 4.2 Ограничения

- нельзя менять Event Store схему
- нельзя менять UoW контракт
- нельзя вводить альтернативные механизмы publish
- нельзя внедрять технические поля в Domain events
- нельзя ослаблять optimistic locking

Любое изменение требует нового ADR.

---

### 4.3 Архитектурные обязательства

После принятия Freeze:

- все новые фичи обязаны соответствовать Freeze
- нарушение Freeze считается архитектурной ошибкой
- CI обязан проверять boundary нарушения
- PR обязан проходить архитектурный чеклист
- любое изменение Freeze требует нового ADR

---

## 5. Enforcement

Freeze контролируется через:

- ADR-0002 (Boundary Contracts)
- ADR-0003 (Architecture Validation Checklist)
- ADR-0004 (CI Boundary Enforcement)
- PR checklist
- Code review

Нарушение фиксируется автоматически (CI) или на ревью.

Изменение Freeze без нового ADR запрещено.

---

## 6. Notes

Core Frozen v1 распространяется только на write-модель.

Read-model (projection, read-store, оптимизации)
могут быть спроектированы в новых ADR,
если они не нарушают write-core.

---

# Acceptance Criteria

- [x] Статус установлен в Accepted
- [x] Freeze охватывает Event Store, UoW, Outbox, Snapshot, Application Rules
- [x] Freeze согласован с Boundary Contracts
- [x] Freeze поддерживается CI enforcement
- [x] Freeze задокументирован как ADR-0001

---

# Lifecycle

Proposed → Accepted  

Изменение Freeze требует нового ADR
(например: ADR-0005-core-v2).

---

# Architectural Integrity Rule

Любое изменение:

- Event Store контракта
- UnitOfWork контракта
- Outbox атомарности
- Snapshot политики
- Application orchestration

требует нового ADR.

Изменение кода без изменения ADR —
архитектурное нарушение.