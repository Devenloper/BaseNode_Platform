# ADR-0009: Projection Version Injection и Immutable Domain Events

Дата: 2026-02-15  
Статус: ACCEPTED  
Связанные ADR: 0001, 0002, 0007  

---

## Контекст

Система использует Event Sourcing и Core Frozen Domain.

Domain Events:

- immutable (`@dataclass(frozen=True)`)
- не изменяются после создания
- не устанавливают aggregate version

Version назначается исключительно Event Store.

Projection слой должен использовать aggregate_version как source of truth.

---

## Проблема

Projection тесты требуют:

- event.version доступен
- Domain Events immutable
- Projection корректно использует version

Прямое изменение:


event.version = 1


нарушает frozen контракт.

---

## Решение

Используется controlled infrastructure-level metadata injection:


object.setattr(event, "version", aggregate_version)


Это допустимо, потому что:

- не нарушает frozen контракт логически
- выполняется вне Domain
- version — metadata, не бизнес-данные

---

## Финальная цепочка ответственности

Domain  
→ генерирует immutable event (version=None)

Event Store  
→ назначает aggregate_version

Outbox  
→ сохраняет aggregate_version

Dispatcher  
→ inject version через object.__setattr__

Projector  
→ использует event.version

---

## Почему это корректно

Domain не знает о version assignment.

Version назначается только infrastructure.

Core Frozen не нарушается.

---

## Последствия

Положительные:

- immutable Domain сохранён
- Projection корректен
- replay работает
- архитектура чистая

Отрицательные:

- infrastructure имеет право metadata injection

---

## Статус

ACCEPTED
Production-ready