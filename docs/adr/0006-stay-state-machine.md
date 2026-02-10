# ADR-0006: Stay Aggregate State Machine

Status: Accepted  
Date: 2026-02-10  
Authors: Architecture Team  
Related ADRs:
- ADR-0001 Core Frozen v1
- ADR-0002 Boundary Contracts
- ADR-0003 Architecture Validation Checklist

---

## 1. Context

Stay является ключевым агрегатом домена проживания.

В процессе проектирования выявлена необходимость
строго формализовать жизненный цикл Stay
для предотвращения:

- разрастания условной логики
- неконтролируемых состояний
- нарушения инвариантов
- деградации Event Sourcing модели

Особое внимание требуется к конфликтам,
переселениям и offline-операциям.

---

## 2. Decision

Принято решение зафиксировать
**строгую state machine модель агрегата Stay**.

### 2.1 Lifecycle States

Stay может находиться **только** в одном из следующих состояний:

- `NOT_STARTED`
- `IN_PROGRESS`
- `COMPLETED`

Другие lifecycle-состояния запрещены.

---

### 2.2 State Transitions

Разрешённые переходы:

| From | Command | To |
|-----|--------|----|
| NOT_STARTED | check_in | IN_PROGRESS |
| IN_PROGRESS | check_out | COMPLETED |
| IN_PROGRESS | relocate | IN_PROGRESS |

Запрещены:

- check_out из NOT_STARTED
- повторный check_in
- любые команды после COMPLETED
- relocate после COMPLETED

---

### 2.3 Conflict Handling

Конфликт **не является lifecycle-состоянием**.

Конфликт моделируется как:

- domain event
- флаг состояния агрегата (`conflict_detected`)
- metadata события (при необходимости)

Запрещено:

- вводить `CONFLICT` как состояние
- использовать конфликт для управления lifecycle

---

### 2.4 Relocation

Relocation:

- не меняет lifecycle
- фиксируется отдельным Domain Event
- может менять room_id
- возможен только в состоянии IN_PROGRESS

---

## 3. Invariants

Агрегат Stay обязан гарантировать:

- check_in возможен только один раз
- check_out возможен только один раз
- ended_at > started_at
- состояние изменяется только через apply()
- version увеличивается только через Domain Events
- lifecycle не может быть изменён напрямую

---

## 4. Consequences

После принятия ADR:

- Backend обязан реализовать агрегат строго по state machine
- Любое добавление состояния требует нового ADR
- Любое ослабление правил считается архитектурным нарушением
- Application слой не имеет права управлять lifecycle логикой

---

## 5. Enforcement

Контроль осуществляется через:

- Code Review
- Architecture Validation Checklist
- ADR compliance
- Domain invariants

Если код противоречит ADR —
он считается дефектным независимо от тестов.

---

## Architectural Integrity Rule

Lifecycle агрегата Stay является частью Core Domain.

Любое изменение lifecycle
требует нового ADR.

Код не может изменять модель без изменения ADR.