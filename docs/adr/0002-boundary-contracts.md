# ADR-0002: Boundary Contracts

Status: Accepted  
Date: 2026-02-09  
Authors: Architecture Team  
Related ADRs: 0001-core-frozen-v1.md, 0003-architecture-validation-checklist.md, 0004-ci-boundary-enforcement.md  
Supersedes: None  

---

## 1. Context

После фиксации Core Frozen v1 стало критически важно
предотвратить постепенную деградацию архитектуры через
нарушение направлений зависимостей.

Наиболее частые риски:

- импорт SQLAlchemy в Domain
- использование FastAPI в Application
- вызов Domain напрямую из Interface
- формирование HTTP-ответов в Infrastructure
- утечка DTO между слоями
- добавление технических полей в Domain

Без формализованных границ слоёв:

- архитектура начинает "размываться"
- ответственность слоёв смешивается
- появляется скрытая связность
- нарушается изоляция Event Sourcing
- Core Frozen v1 теряет enforce’имость

Требуется нормативный документ,
фиксирующий допустимые и запрещённые зависимости.

---

## 2. Decision

Принято решение формализовать и зафиксировать
**Boundary Contracts** между слоями системы.

Система состоит из 4 слоёв:

1. Domain
2. Application
3. Infrastructure
4. Interface (HTTP)

Разрешённое направление зависимостей:

Interface → Application → Domain  
Application → Contracts  
Infrastructure → Domain (только типы агрегатов)

Domain не зависит ни от кого.

---

### 2.1 Domain Boundary

Domain запрещено:

- импортировать Infrastructure
- импортировать Application
- импортировать SQLAlchemy
- импортировать FastAPI
- импортировать Pydantic
- знать о UnitOfWork
- знать о Repository
- знать об EventStore
- знать об Outbox
- знать о Snapshot
- знать о expected_version
- знать о metadata
- знать о correlation_id / causation_id
- выполнять I/O
- использовать системное время
- использовать randomness

Domain разрешено:

- определять агрегаты
- определять Domain events
- определять domain-level команды
- определять domain exceptions
- изменять состояние только через apply()
- хранить version как техническое поле

Domain — единственное место бизнес-инвариантов.

---

### 2.2 Application Boundary

Application запрещено:

- импортировать FastAPI
- импортировать Pydantic
- формировать HTTP-ответы
- использовать JSONResponse
- выполнять SQL напрямую
- создавать AsyncSession
- реализовывать бизнес-инварианты
- изменять состояние агрегата напрямую

Application разрешено:

- оркестрировать use-case
- использовать UnitOfWork
- передавать expected_version
- передавать metadata
- вызывать Domain операции
- выбрасывать:
  - Domain exceptions
  - VersionConflictError
  - GuardError
  - SystemModeError
  - InvalidExpectedVersionError

Application не подавляет эти исключения.

---

### 2.3 Infrastructure Boundary

Infrastructure запрещено:

- импортировать FastAPI
- импортировать Pydantic
- формировать HTTP-ответы
- знать о роутерах
- реализовывать бизнес-логику
- изменять Domain state вне apply()

Infrastructure разрешено:

- реализовывать Repository
- реализовывать UnitOfWork
- реализовывать EventStore
- реализовывать SnapshotStore
- реализовывать Outbox
- выполнять SQL
- управлять транзакциями

Infrastructure не принимает бизнес-решений.

---

### 2.4 Interface Boundary

Interface запрещено:

- импортировать SQLAlchemy
- импортировать EventStore
- импортировать SnapshotStore
- импортировать Outbox
- создавать UnitOfWork вручную
- вызывать Domain методы напрямую
- выполнять commit
- публиковать события
- проверять expected_version
- реализовывать бизнес-инварианты

Interface разрешено:

- создавать Application команды
- вызывать handler
- преобразовывать DTO
- маппить исключения в HTTP
- генерировать causation_id
- получать actor из middleware

Interface не содержит бизнес-логики.

---

### 2.5 DTO Boundary

- Pydantic модели не пересекают границу Application
- Domain dataclasses не пересекают HTTP напрямую
- Infrastructure не использует Pydantic
- Domain не знает о JSON

DTO преобразование происходит только в Interface.

---

### 2.6 Exception Boundary

Разрешённые пересечения:

Domain → Application  
Application → Interface  

VersionConflictError в HTTP обязан возвращать:

{
  "detail": "Version conflict",
  "aggregate_id": "...",
  "expected": X,
  "actual": Y
}

Это представление относится только к Interface.

---

## 3. Rationale

Boundary Contracts:

- защищают Core Frozen v1
- обеспечивают изоляцию Domain
- сохраняют детерминизм replay
- предотвращают смешивание ответственности
- делают архитектуру проверяемой

Без строгих границ:

- CI не может автоматически выявлять нарушения
- code review становится субъективным
- архитектура деградирует постепенно

Boundary Contracts делают правила формальными
и enforce’имыми.

---

## 4. Consequences

### 4.1 Положительные последствия

- слои строго изолированы
- зависимость односторонняя
- архитектура становится проверяемой
- возможно автоматическое CI-enforcement
- снижение когнитивной нагрузки

---

### 4.2 Ограничения

- запрещены "быстрые" обходные решения
- нельзя внедрять инфраструктуру в Domain
- нельзя использовать HTTP-объекты вне Interface
- любые изменения направлений зависимостей требуют нового ADR

---

### 4.3 Архитектурные обязательства

После принятия Boundary Contracts:

- PR обязан проверяться на запрещённые импорты
- CI обязан проверять слои
- Pre-commit обязан блокировать нарушения
- Code review обязан учитывать слоёвую изоляцию
- Нарушение считается архитектурным дефектом

---

## 5. Enforcement

Boundary Contracts enforce’ятся через:

- Architecture Validation Checklist (ADR-0003)
- CI Boundary Enforcement (ADR-0004)
- pre-commit hook
- PR checklist
- обязательный code review

Нарушение импортов должно приводить к CI-failure.

Boundary без enforcement не считаются принятыми.

---

## 6. Notes

Boundary Contracts являются постоянными
в рамках Core Frozen v1.

Изменение направлений зависимостей
требует нового ADR
(например: ADR-000X-boundary-v2).

---

# Acceptance Criteria

- [x] Статус установлен в Accepted
- [x] Контракты слоёв формализованы
- [x] Направления зависимостей зафиксированы
- [x] DTO границы зафиксированы
- [x] Добавлены механизмы enforcement

---

# Lifecycle

Proposed → Accepted  

Изменение Boundary Contracts
требует нового ADR.

---

# Architectural Integrity Rule

Любой импорт, нарушающий
установленные направления зависимостей,
считается архитектурным нарушением.

Код не может противоречить принятому ADR.