# Pull Request Checklist
Core Frozen v1

PR не может быть принят без прохождения этого чеклиста.

---

## 1. Freeze Check

- [ ] Event Store контракт не изменён
- [ ] UnitOfWork контракт не изменён
- [ ] Outbox модель не изменена
- [ ] Snapshot policy не изменена
- [ ] Application Rules соблюдаются
- [ ] Event Naming Conventions соблюдаются
- [ ] Boundary Contracts соблюдаются

---

## 2. Domain Layer (если затронут)

- [ ] Нет новых запрещённых импортов
- [ ] Все бизнес-инварианты находятся только в Domain
- [ ] Нет I/O
- [ ] Нет прямых state-мутаций вне apply()
- [ ] version увеличивается только через apply()

---

## 3. Application Layer (если затронут)

- [ ] Одна команда — один агрегат — одна транзакция
- [ ] expected_version передаётся явно
- [ ] handler не делает commit вручную
- [ ] handler не подавляет Domain exceptions
- [ ] Нет FastAPI / HTTP зависимостей

---

## 4. Infrastructure Layer (если затронут)

- [ ] Append-only соблюдается
- [ ] Нет UPDATE / DELETE в event_store
- [ ] Outbox атомарен
- [ ] Snapshot вторичен
- [ ] Нет HTTP зависимостей

---

## 5. Interface Layer (если затронут)

- [ ] Нет бизнес-логики в endpoint
- [ ] Нет commit
- [ ] Нет вызова Domain напрямую
- [ ] expected_version не проверяется в endpoint
- [ ] Exception mapping корректный

---

## 6. VersionConflict HTTP Mapping

- [ ] VersionConflictError возвращает:
  - aggregate_id
  - expected
  - actual

---

## 7. Red Flags Check

Подтверждаю, что в PR отсутствует:

- [ ] FastAPI в Application
- [ ] SQLAlchemy в Domain
- [ ] commit вне UoW
- [ ] publish без Outbox
- [ ] Infrastructure формирует HTTP
- [ ] Interface вызывает Domain напрямую

---

## Final Confirmation

- [ ] Я проверил PR по docs/architecture_validation_checklist.md
- [ ] Freeze не нарушен
- [ ] Архитектурные границы соблюдены

PR готов к ревью.