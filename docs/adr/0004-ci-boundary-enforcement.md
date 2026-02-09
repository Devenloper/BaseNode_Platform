# ADR-0004: CI Boundary Enforcement

Status: Accepted  
Date: 2026-02-09  
Authors: Architecture Team  
Related ADRs:  
- 0001-core-frozen-v1.md  
- 0002-boundary-contracts.md  
- 0003-architecture-validation-checklist.md  
Supersedes: None  

---

## 1. Context

После фиксации:

- Core Frozen v1 (ADR-0001)
- Boundary Contracts (ADR-0002)
- Architecture Validation Checklist (ADR-0003)

архитектурные правила стали формально определены.

Однако без автоматического enforcement:

- нарушения выявляются только на ревью
- правила могут игнорироваться
- «временные» импорты попадают в main
- архитектура постепенно деградирует
- человеческий фактор становится критичным

Необходим автоматический механизм,
который **блокирует архитектурные нарушения
до попадания кода в protected branch**.

---

## 2. Decision

Принято решение внедрить **CI Boundary Enforcement**
как обязательный архитектурный gate.

CI обязан:

1. Проверять запрещённые импорты между слоями.
2. Блокировать merge при нарушении Boundary Contracts.
3. Работать автоматически на каждом Pull Request.
4. Быть обязательным статус-чеком для protected branch.

CI не является рекомендацией.
CI является блокирующим механизмом.

---

## 3. Scope of Enforcement

CI Boundary Enforcement проверяет:

### 3.1 Нарушения слоёв

Запрещённые направления:

- Domain → Infrastructure
- Domain → Application
- Domain → SQLAlchemy
- Domain → FastAPI
- Application → FastAPI
- Application → SQLAlchemy (напрямую)
- Infrastructure → FastAPI
- Infrastructure → Pydantic
- Interface → SQLAlchemy
- Interface → EventStore
- Interface → Outbox
- Interface → Snapshot

---

### 3.2 Архитектурные инварианты

CI должен гарантировать:

- отсутствие SQLAlchemy в Domain
- отсутствие FastAPI в Application
- отсутствие HTTP-объектов вне Interface
- отсутствие технических зависимостей в Domain

CI не проверяет бизнес-логику.
CI проверяет только архитектурные границы.

---

## 4. Implementation

Enforcement реализуется через:

### 4.1 Pre-commit Hook

- локальная проверка до commit
- раннее обнаружение нарушений
- не заменяет CI

---

### 4.2 CI Job

Обязательный job в pipeline:

architecture-boundary-check


Он:

- запускает скрипт проверки импортов
- анализирует изменённые файлы
- завершает pipeline с exit code 1 при нарушении

---

### 4.3 Branch Protection

Protected branch (например: `main`) обязан иметь:

- Required status checks
- Обязательный `architecture-boundary-check`
- Запрет direct push
- Merge только через Pull Request

Без прохождения CI merge невозможен.

---

## 5. Rationale

CI Boundary Enforcement:

- делает Boundary Contracts enforce’имыми
- защищает Core Frozen v1
- устраняет зависимость от человеческого фактора
- делает архитектуру самозащищающейся
- обеспечивает воспроизводимость контроля

Альтернативы:

- только code review → отвергнуто
- только pre-commit → недостаточно
- ручной аудит → не масштабируется

CI — минимально достаточный автоматический барьер.

---

## 6. Consequences

### 6.1 Положительные последствия

- архитектурные нарушения не попадают в main
- архитектура становится защищённой
- уменьшается когнитивная нагрузка ревью
- повышается дисциплина разработки
- новые разработчики не могут случайно нарушить границы

---

### 6.2 Ограничения

- возможны ложноположительные срабатывания
- требует поддержки скрипта
- увеличивает формальность процесса
- может замедлять merge при ошибках

Ограничения считаются приемлемыми.

---

### 6.3 Архитектурные обязательства

После принятия ADR-0004:

- любой новый слой должен быть добавлен в CI rules
- изменение Boundary Contracts требует обновления CI
- удаление CI enforcement запрещено без нового ADR
- отключение job считается архитектурным нарушением

---

## 7. Non-Goals

CI Boundary Enforcement:

- не проверяет бизнес-логику
- не проверяет корректность SQL
- не проверяет производительность
- не заменяет code review
- не заменяет checklist

CI — это технический gate, а не архитектурный анализатор.

---

## 8. Enforcement Policy

Следующие условия обязательны:

- CI job является required status check
- Merge невозможен при failure
- Direct push в protected branch запрещён
- CI не может быть отключён без нового ADR

Нарушение этих правил считается нарушением Core Frozen v1.

---

## 9. Relation to Other ADRs

- ADR-0001 фиксирует неизменяемое ядро
- ADR-0002 фиксирует границы слоёв
- ADR-0003 фиксирует checklist
- ADR-0004 делает их enforce’имыми

ADR-0004 замыкает архитектурный контур защиты.

---

# Acceptance Criteria

- [x] Статус установлен в Accepted
- [x] CI job добавлен в pipeline
- [x] Job является required status check
- [x] Protected branch настроен
- [x] CI проверяет Boundary Contracts

---

# Lifecycle

Proposed → Accepted  

Удаление или ослабление CI Enforcement
требует нового ADR.

---

# Architectural Integrity Rule

Если архитектурное правило
не enforce’ится автоматически
и может быть обойдено,

оно рано или поздно будет нарушено.

CI — обязательный механизм
самозащиты архитектуры.