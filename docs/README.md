# Документация BaseNode Platform

Версия: 1.0  
Статус: Навигационный документ  
Назначение: Быстрое понимание структуры системы и правил разработки  

---

# 1. О системе

BaseNode Platform — доменно-ориентированная система, построенная на:

- Backend: Python (DDD + Event Sourcing + CQRS)
- Frontend: React
- Разделение интерфейсов:
  - Admin UI (операционный интерфейс)
  - Kiosk UI (гостевой интерфейс)

Архитектура ориентирована на:

- неизменяемую историю
- строгую версионность
- изоляцию доменов
- OFFLINE-устойчивость
- контроль конфликтов

---

# 2. Структура документации

Документация разделена на 4 уровня:

```
docs/
├── architecture/   ← как устроена система
├── governance/     ← как мы с ней работаем
├── adr/            ← почему приняты решения
└── testing/        ← как проверяем корректность
```

---

# 3. Что читать в первую очередь

## Новый разработчик (Backend)

1. architecture/ARCHITECTURE_OVERVIEW.md  
2. architecture/BOUNDED_CONTEXT_MAP.md  
3. governance/AI_ARCHITECTURE_MANIFESTO.md  
4. architecture/EVENT_MODEL_GUIDELINES.md  

---

## Новый разработчик (Frontend)

1. architecture/ARCHITECTURE_OVERVIEW.md  
2. architecture/BOUNDED_CONTEXT_MAP.md  
3. governance/AI_ARCHITECTURE_MANIFESTO.md  
4. architecture/VERSIONING_POLICY.md  

---

## Работа с ИИ

Перед открытием любого доменного чата:

1. governance/DOMAIN_CHAT_TEMPLATE.md  
2. governance/AI_ARCHITECTURE_MANIFESTO.md  
3. architecture/BOUNDED_CONTEXT_MAP.md  

---

# 4. Разделение Backend и Frontend

## Backend (Python)

- Строгая изоляция доменов
- Event Store как источник истины
- Никакого UPDATE состояния
- Только события
- Версионность агрегатов обязательна

См.:
- architecture/PROJECT_STRUCTURE.md
- architecture/VERSIONING_POLICY.md
- testing/TEST_STRATEGY.md

---

## Frontend (React)

Frontend не является источником истины.

Admin UI:
- Управление доменными процессами
- Отображение конфликтов
- Работа с закрытыми периодами
- Разрешение конфликтов

Kiosk UI:
- Упрощённый интерфейс
- Ограниченный набор команд
- Нет прямого изменения доменных агрегатов
- Нет админ-функций

Frontend не содержит бизнес-инвариантов.

---

# 5. Разделение UI

## Admin UI

Предназначен для:

- оператора
- бухгалтера
- управляющего
- HR

Может:
- инициировать команды
- видеть конфликты
- разрешать конфликты
- инициировать компенсации

Не может:
- переписывать историю
- редактировать события
- обходить закрытые периоды

---

## Kiosk UI

Предназначен для:

- гостя

Может:
- инициировать ограниченные команды
- работать в ограниченном OFFLINE-режиме

Не может:
- видеть финансовые детали
- разрешать конфликты
- менять исторические данные

---

# 6. Принцип доменной изоляции

Каждый домен:

- развивается отдельно
- имеет отдельный ИИ-чат
- не импортирует код другого домена

Кросс-доменное взаимодействие — только через события.

См.:
- architecture/BOUNDED_CONTEXT_MAP.md

---

# 7. Как работать с несколькими ИИ-чатами

Один домен = один чат.

Отдельный чат:

- Booking
- Finance 5A
- Finance 5B
- Loyalty
- HR
- Unit
- DGU
- Integrations
- Offline / Reconciliation
- Core Architecture

Запрещено смешивать домены в одном чате.

---

# 8. Изменение архитектуры

Любое изменение:

- Event Store
- Версионности
- Источника истины
- OFFLINE-логики
- Компенсационной модели

Требует:

1. ADR
2. Обновления документации
3. Проверки Versioning Policy

---

# 9. Приоритеты системы

1. Целостность истории
2. Версионная дисциплина
3. Отсутствие двойной истины
4. Предсказуемость OFFLINE
5. Производительность
6. UX

---

# 10. Порядок дальнейшей проработки документации

С учётом Python + React + Admin UI + Kiosk UI:

Следующий документ должен быть:

1. architecture/ARCHITECTURE_OVERVIEW.md (с учётом UI-слоёв)  
2. architecture/BOUNDED_CONTEXT_MAP.md  
3. architecture/PROJECT_STRUCTURE.md (Python + frontend repo структура)  
4. governance/DEVELOPMENT_WORKFLOW.md (модель нескольких ИИ-чатов + Git flow)

---

# 11. Главный принцип

История неизменяема.  
Архитектура важнее скорости.  
ИИ — инструмент, не архитектор.