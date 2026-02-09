# Architecture Validation Checklist
Core Frozen v1

Документ предназначен для регулярной проверки
соответствия реализации утверждённой архитектуре.

Используется:

- при code review
- при добавлении новых фич
- перед релизом
- при рефакторинге
- при аудите архитектуры

Нарушение любого пункта считается архитектурным дефектом.

---

# 1. Общая проверка Freeze

□ Event Store контракт не изменён  
□ UnitOfWork контракт не изменён  
□ Outbox модель не изменена  
□ Snapshot policy не изменена  
□ Application Rules соблюдаются  
□ Event Naming Conventions соблюдаются  
□ Boundary Contracts соблюдаются  

---

# 2. Domain Layer Checklist

## 2.1 Зависимости

□ Domain не импортирует SQLAlchemy  
□ Domain не импортирует FastAPI  
□ Domain не импортирует Pydantic  
□ Domain не импортирует Infrastructure  
□ Domain не импортирует Application  

## 2.2 Поведение

□ Все бизнес-инварианты находятся только в Domain  
□ Aggregate изменяет состояние только через apply()  
□ Нет прямых state-мутаций вне apply()  
□ Нет I/O в Domain  
□ Нет обращения к системному времени  
□ Нет randomness  

## 2.3 События

□ События не содержат технических полей  
□ Нет metadata в Domain events  
□ Нет aggregate_version в Domain events  
□ Названия событий соответствуют naming rules  

## 2.4 Версионная модель

□ version увеличивается при каждом apply  
□ replay детерминирован  
□ Aggregate не знает об expected_version  

---

# 3. Application Layer Checklist

## 3.1 Зависимости

□ Application не импортирует FastAPI  
□ Application не импортирует SQLAlchemy напрямую  
□ Application не формирует HTTP-ответы  
□ Application не использует JSONResponse  

## 3.2 Orchestration

□ Одна команда — один агрегат — одна транзакция  
□ expected_version передаётся явно  
□ handler не вычисляет version  
□ handler не подавляет Domain exceptions  
□ handler не делает commit вручную  
□ commit только в __aexit__  

## 3.3 Транзакции

□ Нет commit вне UnitOfWork  
□ Нет publish до commit  
□ Outbox используется для публикации  
□ Нет вызова EventStore напрямую из handler  

## 3.4 Guards

□ Guards не содержат бизнес-инвариантов  
□ Guards не изменяют состояние  
□ Guards вызываются до Domain операции  

---

# 4. Infrastructure Layer Checklist

## 4.1 Зависимости

□ Infrastructure не импортирует FastAPI  
□ Infrastructure не импортирует Pydantic  
□ Infrastructure не формирует HTTP-ответы  

## 4.2 Repository

□ Repository не содержит бизнес-логики  
□ Repository не принимает решений  
□ Repository использует EventStore для append  
□ Repository выполняет replay детерминированно  

## 4.3 Event Store

□ Append-only соблюдается  
□ Нет UPDATE event_store  
□ Нет DELETE event_store  
□ UNIQUE (aggregate_id, aggregate_version) существует  
□ IntegrityError маппится в VersionConflictError  

## 4.4 Outbox

□ Outbox пишется в той же транзакции  
□ Нет отдельного commit внутри Outbox  
□ publish выполняется воркером  
□ publish идемпотентен  

## 4.5 Snapshot

□ Snapshot вторичен  
□ Snapshot сохраняется после commit  
□ Ошибка snapshot не ломает события  
□ Snapshot можно удалить без потери данных  

---

# 5. Interface Layer Checklist

## 5.1 Зависимости

□ Interface не импортирует SQLAlchemy  
□ Interface не импортирует EventStore  
□ Interface не импортирует Outbox  
□ Interface не создаёт UnitOfWork вручную  

## 5.2 Endpoint

□ Endpoint не содержит бизнес-логики  
□ Endpoint не выполняет commit  
□ Endpoint не вызывает Domain напрямую  
□ Endpoint не проверяет expected_version  
□ Endpoint не ловит Domain exceptions  

## 5.3 Exception Mapping

□ DomainError → 400  
□ InvalidExpectedVersionError → 400  
□ VersionConflictError → 409  
□ GuardError → 403  
□ SystemModeError → 503  

□ VersionConflictError возвращает:
  - aggregate_id
  - expected
  - actual

---

# 6. Dependency Direction Check

Разрешённые направления:

□ Interface → Application  
□ Application → Domain  
□ Application → Contracts  
□ Infrastructure → Domain (только типы)  

Запрещено:

□ Domain → любой слой  
□ Infrastructure → Interface  
□ Application → FastAPI  
□ Interface → SQLAlchemy  

---

# 7. Event Sourcing Integrity

□ Replay полностью определяет состояние  
□ Нет побочных эффектов при apply  
□ Aggregate не знает о механике хранения  
□ expected_version обязателен при save  
□ VersionConflict не подавляется  

---

# 8. Конкурентность

□ Optimistic locking реализован  
□ expected_version сравнивается  
□ IntegrityError корректно обрабатывается  
□ Нет advisory lock  
□ Нет глобальных блокировок  

---

# 9. Read Model (v1)

□ GET не создаёт событий  
□ GET не использует UnitOfWork  
□ GET не использует CommandHandler  
□ GET интерпретирует status=None как 404  
□ GET не добавляет новую инфраструктуру  

---

# 10. Code Review Red Flags

Если обнаружено хотя бы одно:

- импорт FastAPI в Application
- SQLAlchemy в Domain
- бизнес-логика в Guards
- commit вне UoW
- publish без Outbox
- изменение event_store
- handler с try/except DomainError
- Interface вызывает Domain напрямую
- Infrastructure формирует HTTP

→ Требуется немедленный архитектурный аудит.

---

# 11. Final Integrity Gate

Перед релизом убедиться:

□ Все пункты пройдены  
□ Freeze не нарушен  
□ Boundary Contracts соблюдены  
□ Нет "временных" обходов  
□ Нет технического долга в ядре  

---

# Заключение

Этот чеклист — механизм предотвращения деградации архитектуры.

Каждая новая фича обязана проходить через него.

Архитектура защищается не кодом,
а дисциплиной.