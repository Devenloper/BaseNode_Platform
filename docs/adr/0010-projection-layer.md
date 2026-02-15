# ADR-0010: Projection Layer Architecture

Дата: 2026-02-15  
Статус: ACCEPTED  

---

## Назначение

Projection слой строит read-model из Domain Events.

Projection не влияет на Domain.

Projection может быть полностью пересоздан.

---

## Компоненты

projection/

    projector.py
    repository.py
    models.py

infrastructure/outbox/

    dispatcher.py

---

## Поток

OutboxRecord
→ Dispatcher
→ Projector
→ ProjectionRepository
→ stay_read_model

---

## Правила

Projection:

НЕ импортирует domain aggregate  
НЕ изменяет domain  
НЕ влияет на Event Store  

Projection:

использует aggregate_version как version

---

## Гарантии

Projection idempotent  
Projection replayable  
Projection stateless  

---

## Статус

Production ready