import pytest
from uuid import uuid4
from datetime import datetime, timedelta

from domain.stay.aggregate import (
    Stay,
    StayLifecycle,
    StayAlreadyCheckedInError,
    StayNotStartedError,
    StayAlreadyCheckedOutError,
    StayCompletedError,
    InvalidStayPeriodError,
    InvalidRelocationError,
)
from domain.stay.events import (
    StayCheckedIn,
    StayCheckedOut,
    StayRelocated,
)


# ============================================================
# Helpers
# ============================================================

def now():
    return datetime.utcnow()


# ============================================================
# Lifecycle transitions
# ============================================================

def test_initial_state():
    stay = Stay(uuid4())
    assert stay.lifecycle == StayLifecycle.NOT_STARTED
    assert stay._version == 0
    assert stay.room_id is None


def test_check_in_moves_to_in_progress():
    stay = Stay(uuid4())

    stay.check_in(room_id=uuid4(), started_at=now())

    assert stay.lifecycle == StayLifecycle.IN_PROGRESS
    assert stay._version == 1


def test_check_out_moves_to_completed():
    stay = Stay(uuid4())
    start = now()
    end = start + timedelta(hours=1)

    stay.check_in(room_id=uuid4(), started_at=start)
    stay.check_out(ended_at=end)

    assert stay.lifecycle == StayLifecycle.COMPLETED
    assert stay._version == 2


def test_relocate_keeps_lifecycle_in_progress():
    stay = Stay(uuid4())
    start = now()

    stay.check_in(room_id=uuid4(), started_at=start)
    stay.relocate(new_room_id=uuid4(), relocated_at=start)

    assert stay.lifecycle == StayLifecycle.IN_PROGRESS
    assert stay._version == 2


# ============================================================
# Invalid transitions
# ============================================================

def test_check_in_only_once():
    stay = Stay(uuid4())
    stay.check_in(room_id=uuid4(), started_at=now())

    with pytest.raises(StayAlreadyCheckedInError):
        stay.check_in(room_id=uuid4(), started_at=now())


def test_check_out_without_check_in():
    stay = Stay(uuid4())

    with pytest.raises(StayNotStartedError):
        stay.check_out(ended_at=now())


def test_check_out_only_once():
    stay = Stay(uuid4())
    start = now()
    end = start + timedelta(hours=1)

    stay.check_in(room_id=uuid4(), started_at=start)
    stay.check_out(ended_at=end)

    with pytest.raises(StayAlreadyCheckedOutError):
        stay.check_out(ended_at=end + timedelta(hours=1))


def test_relocate_only_in_progress():
    stay = Stay(uuid4())

    with pytest.raises(StayNotStartedError):
        stay.relocate(new_room_id=uuid4(), relocated_at=now())


def test_no_commands_after_completed():
    stay = Stay(uuid4())
    start = now()
    end = start + timedelta(hours=1)

    stay.check_in(room_id=uuid4(), started_at=start)
    stay.check_out(ended_at=end)

    with pytest.raises(StayCompletedError):
        stay.relocate(new_room_id=uuid4(), relocated_at=end)


# ============================================================
# Invariants
# ============================================================

def test_ended_at_must_be_after_started_at():
    stay = Stay(uuid4())
    start = now()

    stay.check_in(room_id=uuid4(), started_at=start)

    with pytest.raises(InvalidStayPeriodError):
        stay.check_out(ended_at=start)


def test_relocation_requires_different_room():
    stay = Stay(uuid4())
    start = now()
    room = uuid4()

    stay.check_in(room_id=room, started_at=start)

    with pytest.raises(InvalidRelocationError):
        stay.relocate(new_room_id=room, relocated_at=start)


# ============================================================
# Version semantics
# ============================================================

def test_version_increments_strictly_by_events():
    stay = Stay(uuid4())
    start = now()
    end = start + timedelta(hours=1)

    assert stay._version == 0

    stay.check_in(room_id=uuid4(), started_at=start)
    assert stay._version == 1

    stay.relocate(new_room_id=uuid4(), relocated_at=start)
    assert stay._version == 2

    stay.check_out(ended_at=end)
    assert stay._version == 3


def test_replay_increments_version():
    stay_id = uuid4()
    start = now()
    end = start + timedelta(hours=1)

    events = [
        StayCheckedIn(stay_id=stay_id, room_id=uuid4(), started_at=start),
        StayCheckedOut(stay_id=stay_id, ended_at=end),
    ]

    stay = Stay(stay_id)
    stay.replay(events)

    assert stay._version == 2


# ============================================================
# Replay determinism
# ============================================================

def test_replay_restores_full_state():
    stay_id = uuid4()
    room1 = uuid4()
    room2 = uuid4()
    start = now()
    end = start + timedelta(hours=1)

    events = [
        StayCheckedIn(stay_id=stay_id, room_id=room1, started_at=start),
        StayRelocated(stay_id=stay_id, new_room_id=room2, relocated_at=start),
        StayCheckedOut(stay_id=stay_id, ended_at=end),
    ]

    stay = Stay(stay_id)
    stay.replay(events)

    assert stay.lifecycle == StayLifecycle.COMPLETED
    assert stay.room_id == room2
    assert stay.started_at == start
    assert stay.ended_at == end
    assert stay._version == 3


def test_replay_does_not_create_uncommitted_events():
    stay_id = uuid4()
    start = now()

    events = [
        StayCheckedIn(stay_id=stay_id, room_id=uuid4(), started_at=start),
    ]

    stay = Stay(stay_id)
    stay.replay(events)

    assert stay.get_uncommitted_events() == []
    assert stay._version == 1