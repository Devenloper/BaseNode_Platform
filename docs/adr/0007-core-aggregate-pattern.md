# ADR-0007: Core Aggregate Pattern (Event-Sourced Aggregate Standard)

Status: Accepted  
Date: 2026-02-10  
Authors: Architecture Team  

Related ADRs:
- ADR-0001 Core Frozen v1
- ADR-0002 Boundary Contracts
- ADR-0006 Stay Aggregate State Machine

---

## 1. Context

После реализации первого агрегата Stay (ADR-0006)
сформирован устойчивый шаблон event-sourced агрегата.

Без формализации существует риск:

- расхождения реализации агрегатов
- различной семантики version
- различной replay логики
- появления isinstance-ветвлений
- нарушения deterministic replay
- деградации Core Model

Необходимо зафиксировать единый Core Aggregate Pattern.

---

## 2. Decision

Все агрегаты Core обязаны соответствовать
следующему обязательному стандарту реализации.

---

## 3. Construction Rules

### 3.1 Начальное состояние

Агрегат обязан:

- иметь корректное начальное lifecycle
- не использовать None вместо допустимого state
- инициализировать `_version = 0`
- инициализировать `_uncommitted_events = []`
- фиксировать `_handlers` в `__init__`

Пример:

    def __init__(self, aggregate_id: UUID):
        self.id = aggregate_id
        self._version = 0
        self._uncommitted_events = []
        self._handlers = {...}

---

## 4. Event Sourcing Semantics

### 4.1 State Mutation

Состояние изменяется только через `apply()`.

Запрещено:

- менять lifecycle напрямую
- менять version вручную
- мутировать состояние вне apply-handler

Допустимый поток:

Command → Domain Event → apply() → handler → state mutation

---

### 4.2 Version Semantics (Non-negotiable)

- `_version` увеличивается только в apply()
- `_version` увеличивается при replay
- `_version` никогда не задаётся извне
- `_version` не хранится в Domain Events
- `_version` не передаётся через конструктор

Пример:

    def apply(self, event):
        handler = self._handlers[type(event)]
        handler(event)
        self._version += 1

---

### 4.3 Replay Semantics

Replay обязан:

- быть детерминированным
- не иметь побочных эффектов
- не изменять `_uncommitted_events`
- не зависеть от времени или окружения

Пример:

    def replay(self, events):
        for event in events:
            self.apply(event)

---

## 5. Handler Table Pattern (Mandatory)

Обязательное использование таблицы handler'ов:

    self._handlers = {
        EventType: self._apply_event_type,
    }

Запрещено:

- isinstance
- if/elif цепочки
- строковой dispatch
- reflection-based dispatch

Отсутствие handler → DomainError.

---

## 6. Uncommitted Events Contract

Агрегат обязан:

- хранить `_uncommitted_events`
- добавлять события только через `_record_event`
- очищать события через `clear_uncommitted_events()`
- не модифицировать список извне

Пример:

    def _record_event(self, event):
        self.apply(event)
        self._uncommitted_events.append(event)

---

## 7. Domain Events Constraints

Domain Events обязаны:

- быть `@dataclass(frozen=True)`
- содержать только бизнес-данные
- не содержать metadata
- не содержать aggregate_version
- не содержать технических полей

Domain Event = Business fact only.

---

## 8. Boundary Compliance

Aggregate обязан:

- не знать о Repository
- не знать о UnitOfWork
- не знать о Outbox
- не знать о SQLAlchemy
- не знать о HTTP
- не знать о Application Layer

Любая утечка = нарушение ADR-0002.

---

## 9. Determinism Requirement

Агрегат обязан быть:

- полностью детерминированным
- воспроизводимым через replay
- независимым от инфраструктуры
- независимым от окружения

---

## 10. Non-Goals

ADR-0007:

- не описывает конкретные агрегаты
- не меняет ADR-0006
- не вводит новые состояния
- не изменяет Core Frozen v1

Он фиксирует реализационный стандарт агрегатов.

---

## 11. Consequences

После принятия ADR-0007:

- любой новый агрегат обязан соответствовать pattern
- отклонение требует нового ADR
- изменение version semantics требует нового ADR
- изменение replay semantics требует нового ADR

---

## Architectural Integrity Rule

Если агрегаты реализованы по-разному —
Core Domain теряет целостность.

Core Aggregate Pattern обязателен.

Его изменение возможно только через новый ADR.