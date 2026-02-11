# ADR-0008: Allow tests Root Directory

Status: Accepted  
Date: 2026-02-10  

Related ADRs:
- ADR-0005 Repository Structure Lock

---

## Context

В процессе разработки добавлена директория `tests/`
для unit и integration тестирования.

ADR-0005 зафиксировал структуру root-директорий,
однако `tests/` не был включён в разрешённый список.

---

## Decision

Разрешить root-директорию:

- tests/

Тесты являются частью архитектурной дисциплины
и не считаются нарушением структуры.

---

## Consequences

- Architecture Gate должен разрешать `tests/`
- Другие новые root-директории по-прежнему запрещены