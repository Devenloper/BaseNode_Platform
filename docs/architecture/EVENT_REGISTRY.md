# EVENT_REGISTRY.md
BaseNode Platform  
Версия: 1.0  
Статус: Нормативный реестр  

---

# 1. Назначение

Настоящий документ является официальным реестром всех доменных событий системы.

Если событие отсутствует в данном реестре:
→ оно не существует в архитектуре.

Любое новое событие должно быть:

1. Добавлено в данный реестр
2. Согласовано с Core Architecture Guardian
3. Зафиксировано через ADR (если влияет на архитектуру)

---

# 2. Правила ведения реестра

## 2.1 Обязательные поля

Каждое событие должно иметь:

- event_type
- версия (v1, v2, ...)
- агрегат
- домен
- краткое описание
- кто имеет право создавать
- кто может реагировать
- требует ли компенсации
- breaking_change (да/нет)

---

## 2.2 Версионирование

- Новая версия события создаётся как новая строка.
- Старые версии не удаляются.
- breaking_change = YES требует ADR.

---

## 2.3 Запрещено

- Удалять событие из реестра
- Переименовывать event_type
- Изменять версию задним числом
- Добавлять событие без согласования с Core

---

# 3. Формат записи

| event_type | version | aggregate | domain | description | created_by | listeners | compensation_required | breaking_change |
|------------|----------|-----------|--------|-------------|------------|------------|-----------------------|------------------|

---

# 4. Базовый реестр событий

---

## 4.1 Общесистемные события

| event_type | version | aggregate | domain | description | created_by | listeners | compensation_required | breaking_change |
|------------|----------|-----------|--------|-------------|------------|------------|-----------------------|------------------|
| ConcurrencyConflictDetected | v1 | Any | Core | Конфликт версий агрегата | Core | Audit | No | No |
| OverrideApplied | v1 | Any | Core | Административный override | Any Domain | Audit | No | No |
| ConflictResolutionApplied | v1 | Conflict | Core | Разрешение конфликта | Admin | Related Domain | No | No |

---

## 4.2 Booking

| event_type | version | aggregate | domain | description | created_by | listeners | compensation_required | breaking_change |
|------------|----------|-----------|--------|-------------|------------|------------|-----------------------|------------------|
| BookingCreated | v1 | Booking | Booking | Создано бронирование (из PMS) | PMS Import | Finance, Unit | No | No |
| BookingUpdated | v1 | Booking | Booking | Обновление данных брони | PMS Import | Finance | No | No |
| BookingCancelled | v1 | Booking | Booking | Отмена брони | PMS Import | Finance, Unit | No | No |
| BookingAutoCancelled | v1 | Booking | Booking | Автоотмена по таймеру | Timer | Finance | No | No |
| CheckInPerformed | v1 | Booking | Booking | Выполнен заезд | Booking Domain | Unit, Finance | No | No |
| CheckOutPerformed | v1 | Booking | Booking | Выполнен выезд | Booking Domain | Unit, Loyalty | No | No |
| CheckInRejected | v1 | Booking | Booking | Отказ в заезде | Booking Domain | Audit | No | No |

---

## 4.3 Payment / Accommodation

| event_type | version | aggregate | domain | description | created_by | listeners | compensation_required | breaking_change |
|------------|----------|-----------|--------|-------------|------------|------------|-----------------------|------------------|
| AccommodationPaymentRecorded | v1 | Booking | Finance | Зафиксирован платёж проживания | Finance | PMS Sync | No | No |
| AccommodationPaymentSynced | v1 | Booking | Finance | Синхронизация оплаты из PMS | PMS Import | Analytics | No | No |
| AccommodationRefundProcessed | v1 | Booking | Finance | Возврат по проживанию | Finance | Audit | Yes | No |
| PaymentConflictDetected | v1 | Booking | Finance | Конфликт оплаты | Finance | Task | No | No |

---

## 4.4 Guest

| event_type | version | aggregate | domain | description | created_by | listeners | compensation_required | breaking_change |
|------------|----------|-----------|--------|-------------|------------|------------|-----------------------|------------------|
| GuestCreated | v1 | Guest | Guest | Создание гостя | Guest Domain | Booking | No | No |
| GuestPassportUpdated | v1 | Guest | Guest | Изменение паспортных данных | Guest Domain | Audit | No | No |
| ConsentRecorded | v1 | Guest | Guest | Зафиксировано согласие на ПДн | Guest Domain | Booking | No | No |
| RiskStatusChanged | v1 | Guest | Risk | Изменён статус риска | Risk Domain | Booking | No | No |
| GuestIssueCreated | v1 | GuestIssue | Risk | Создана претензия | Reception/Admin | Risk | No | No |

---

## 4.5 Unit

| event_type | version | aggregate | domain | description | created_by | listeners | compensation_required | breaking_change |
|------------|----------|-----------|--------|-------------|------------|------------|-----------------------|------------------|
| UnitBlocked | v1 | Unit | Unit | Номер заблокирован | Admin | Booking | No | No |
| UnitMaintenanceStarted | v1 | Unit | Unit | Начат ремонт | Engineer | Booking | No | No |
| CleaningCompleted | v1 | Unit | Unit | Уборка завершена | Housekeeping | Booking | No | No |
| UnitConflictDetected | v1 | Unit | Unit | Конфликт назначения | Unit Domain | Task | No | No |

---

## 4.6 Services

| event_type | version | aggregate | domain | description | created_by | listeners | compensation_required | breaking_change |
|------------|----------|-----------|--------|-------------|------------|------------|-----------------------|------------------|
| ServiceItemCreated | v1 | ServiceItem | Service | Создана услуга | Admin | — | No | No |
| ChargeCreated | v1 | Charge | Service | Создана продажа | Reception | Finance | No | No |
| ChargePaid | v1 | Charge | Service | Продажа оплачена | Reception | Loyalty | No | No |
| ChargeRefunded | v1 | Charge | Service | Возврат по услуге | Reception | Finance | Yes | No |

---

## 4.7 Loyalty

| event_type | version | aggregate | domain | description | created_by | listeners | compensation_required | breaking_change |
|------------|----------|-----------|--------|-------------|------------|------------|-----------------------|------------------|
| LoyaltyPointsAccrued | v1 | LoyaltyAccount | Loyalty | Начислены баллы | Loyalty Domain | Analytics | No | No |
| LoyaltyPointsSpent | v1 | LoyaltyAccount | Loyalty | Списаны баллы | Loyalty Domain | Finance | No | No |

---

## 4.8 HR

| event_type | version | aggregate | domain | description | created_by | listeners | compensation_required | breaking_change |
|------------|----------|-----------|--------|-------------|------------|------------|-----------------------|------------------|
| EmployeeCreated | v1 | Employee | HR | Создан сотрудник | Admin | HR | No | No |
| WorkEventRecorded | v1 | Employee | HR | Зафиксировано рабочее время | HR | Timesheet | No | No |
| FinancialPeriodClosed | v1 | Finance | Finance | Закрыт финансовый период | Admin | Finance | No | No |

---

# 5. Правило добавления нового события

Перед добавлением нового события необходимо:

1. Проверить, что оно не дублирует существующее
2. Проверить, что это действительно новый факт
3. Проверить, что не требуется новая версия существующего события
4. Согласовать с Core Guardian
5. Добавить запись в реестр
6. Обновить версию документа

---

# 6. Главный принцип

Event Registry — это карта истории системы.

Если событие не зарегистрировано,
архитектура считается нарушенной.