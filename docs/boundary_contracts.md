# Boundary Contracts
Core Frozen v1

Документ фиксирует жёсткие границы между слоями системы.

Документ является нормативным.
Нарушение считается архитектурной ошибкой.

Core Frozen v1 не подлежит изменению.
Данный документ закрепляет допустимые зависимости и запрещённые импорты.

---

# 1. Цель документа

Зафиксировать:

- допустимые направления зависимостей
- типы исключений, пересекающие границы
- допустимые DTO
- запрещённые импорты
- инварианты слоёв

Документ предотвращает архитектурную деградацию.

---

# 2. Слои системы

Система состоит из 4 слоёв:

1. Domain
2. Application
3. Infrastructure
4. Interface (HTTP)

Зависимости разрешены только в одном направлении:

Interface → Application → Domain  
Application → Contracts → Infrastructure (реализация через DI)

Domain не зависит ни от кого.

---

# 3. Domain Boundary

## 3.1 Domain запрещено

Domain не имеет права:

- импортировать Infrastructure
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
- использовать время системы
- использовать randomness

## 3.2 Domain разрешено

Domain может:

- использовать dataclasses
- определять события
- определять команды (domain-level)
- определять domain exceptions
- генерировать события
- изменять состояние только через apply()
- хранить version как техническое поле
- выбрасывать только DomainError и наследников

## 3.3 Domain инвариант

Domain — единственное место бизнес-инвариантов.

Application не дублирует бизнес-правила.

---

# 4. Application Boundary

Application — orchestration слой.

## 4.1 Application запрещено

Application не имеет права:

- импортировать SQLAlchemy напрямую
- создавать AsyncSession
- выполнять SQL
- импортировать FastAPI
- использовать JSONResponse
- знать о HTTP
- знать о Pydantic
- реализовывать бизнес-инварианты
- изменять состояние агрегата напрямую

## 4.2 Application разрешено

Application может:

- импортировать Domain
- импортировать контракты (Repository, UoW)
- использовать Guards
- управлять транзакцией через UnitOfWork
- передавать expected_version
- передавать metadata
- выбрасывать:
  - Domain exceptions
  - VersionConflictError
  - GuardError
  - SystemModeError
  - InvalidExpectedVersionError

Application не подавляет эти исключения.

## 4.3 Инварианты Application

- Одна команда — один агрегат — одна транзакция
- commit только в __aexit__
- publish только через Outbox
- handler не ловит Domain exceptions
- handler не делает commit вручную

---

# 5. Infrastructure Boundary

Infrastructure реализует контракты.

## 5.1 Infrastructure запрещено

Infrastructure не имеет права:

- импортировать FastAPI
- импортировать Pydantic
- формировать HTTP-ответы
- знать о роутерах
- реализовывать бизнес-логику
- изменять Domain state вне apply()

## 5.2 Infrastructure разрешено

Infrastructure может:

- реализовывать Repository
- реализовывать UnitOfWork
- реализовывать EventStore
- реализовывать SnapshotStore
- реализовывать Outbox
- выполнять SQL
- управлять транзакциями

Infrastructure не принимает бизнес-решений.

---

# 6. Interface Boundary

Interface — HTTP адаптер.

## 6.1 Interface запрещено

Interface не имеет права:

- импортировать SQLAlchemy
- импортировать EventStore
- импортировать SnapshotStore
- импортировать Outbox
- создавать UnitOfWork вручную
- работать с Repository напрямую (кроме read)
- вызывать Domain-методы
- выполнять commit
- выполнять publish
- реализовывать бизнес-валидацию
- проверять expected_version

## 6.2 Interface разрешено

Interface может:

- создавать Application команды
- вызывать handler
- преобразовывать DTO
- маппить исключения в HTTP
- генерировать causation_id
- получать actor из middleware

Interface не содержит бизнес-логики.

---

# 7. Исключения и пересечение границ

## 7.1 Domain → Application

Разрешены только DomainError и наследники.

## 7.2 Application → Interface

Разрешены:

- BookingDomainError
- InvalidExpectedVersionError
- VersionConflictError
- GuardError
- SystemModeError

Interface маппит их в HTTP.

## 7.3 VersionConflict HTTP Mapping

VersionConflictError должен возвращать:

{
  "detail": "Version conflict",
  "aggregate_id": "...",
  "expected": X,
  "actual": Y
}

Это чисто HTTP-представление.
Write-модель не изменяется.

---

# 8. DTO Boundary

- Pydantic модели не пересекают границу Application
- Domain dataclasses не пересекают HTTP напрямую
- Infrastructure не использует Pydantic
- Domain не знает о JSON

DTO преобразование происходит только в Interface.

---

# 9. Dependency Rule

Разрешённые направления импортов:

Interface → Application  
Application → Domain  
Application → Contracts  
Infrastructure → Domain (только для типов агрегатов)  

Запрещено:

Domain → любой другой слой  
Infrastructure → Interface  
Application → FastAPI  
Interface → SQLAlchemy  

---

# 10. Event Sourcing Boundary

- EventStore не знает о Domain инвариантах
- Repository выполняет replay
- Snapshot вторичен
- Outbox атомарен
- commit централизован

Domain не знает о механике хранения событий.

---

# 11. Freeze-гарантия

Core Frozen v1 означает:

- контракт EventStore неизменяем
- контракт UnitOfWork неизменяем
- Outbox-модель неизменяема
- Snapshot policy неизменяема
- Application Rules неизменяемы
- Event Naming Conventions неизменяемы

Boundary Contracts дополняют Freeze,
но не изменяют его.

---

# 12. Архитектурная проверка корректности

Система корректна, если:

- ни один слой не импортирует запрещённые зависимости
- бизнес-инварианты находятся только в Domain
- Interface не содержит логики
- Application не знает о HTTP
- Infrastructure не знает о HTTP
- Domain полностью изолирован

---

# 13. Заключение

Границы — главный механизм защиты архитектуры.

Большинство архитектурных деградаций
начинается с одного "маленького" импорта.

Данный документ фиксирует:

- направления зависимостей
- допустимые исключения
- границы DTO
- запреты на утечку логики

Соблюдение обязательно.