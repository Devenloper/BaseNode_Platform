import pytest
from uuid import uuid4, UUID
from datetime import datetime, timezone, timedelta

from domain.stay.aggregate import Stay
from domain.stay.events import (
    StayCheckedIn,
    StayCheckedOut,
    StayRelocated,
)


def now():
    return datetime.now(timezone.utc)


# ============================================================
# Initial state
# ============================================================

def test_initial_state():
    stay = Stay(uuid4())

    assert stay.room_id is None
    assert stay.started_at is None
    assert stay.ended_at is None
    assert stay.version == 0


# ============================================================
# Check-in
# ============================================================

def test_check_in_sets_state_and_creates_event():
    stay = Stay(uuid4())
    start = now()

    stay.check_in(room_id="101", started_at=start)

    assert stay.room_id == "101"
    assert stay.started_at == start
    assert stay.version == 1

    events = stay.get_uncommitted_events()
    assert len(events) == 1
    assert isinstance(events[0], StayCheckedIn)


def test_check_in_requires_timezone():
    stay = Stay(uuid4())

    with pytest.raises(ValueError):
        stay.check_in(
            room_id="101",
            started_at=datetime.now(),  # naive datetime
        )


def test_check_in_only_once():
    stay = Stay(uuid4())
    stay.check_in(room_id="101", started_at=now())

    with pytest.raises(ValueError):
        stay.check_in(room_id="102", started_at=now())


# ============================================================
# Check-out
# ============================================================

def test_check_out_sets_state_and_creates_event():
    stay = Stay(uuid4())
    start = now()
    end = start + timedelta(hours=1)

    stay.check_in(room_id="101", started_at=start)
    stay.check_out(ended_at=end)

    assert stay.ended_at == end
    assert stay.version == 2

    events = stay.get_uncommitted_events()
    assert len(events) == 2
    assert isinstance(events[1], StayCheckedOut)


def test_check_out_requires_active_stay():
    stay = Stay(uuid4())

    with pytest.raises(ValueError):
        stay.check_out(ended_at=now())


def test_check_out_requires_timezone():
    stay = Stay(uuid4())
    stay.check_in(room_id="101", started_at=now())

    with pytest.raises(ValueError):
        stay.check_out(ended_at=datetime.now())  # naive


# ============================================================
# Relocate
# ============================================================

def test_relocate_changes_room_and_creates_event():
    stay = Stay(uuid4())
    stay.check_in(room_id="101", started_at=now())

    relocated_at = now()

    stay.relocate(
        new_room_id="202",
        relocated_at=relocated_at,
    )

    assert stay.room_id == "202"
    assert stay.version == 2

    events = stay.get_uncommitted_events()
    assert isinstance(events[-1], StayRelocated)


def test_relocate_requires_active_stay():
    stay = Stay(uuid4())

    with pytest.raises(ValueError):
        stay.relocate(
            new_room_id="202",
            relocated_at=now(),
        )


def test_relocate_requires_timezone():
    stay = Stay(uuid4())
    stay.check_in(room_id="101", started_at=now())

    with pytest.raises(ValueError):
        stay.relocate(
            new_room_id="202",
            relocated_at=datetime.now(),  # naive
        )


# ============================================================
# Replay
# ============================================================

def test_replay_restores_state():
    stay_id = uuid4()
    start = now()
    end = start + timedelta(hours=1)

    events = [
        StayCheckedIn(
            stay_id=stay_id,
            room_id="101",
            started_at=start,
        ),
        StayCheckedOut(
            stay_id=stay_id,
            ended_at=end,
        ),
    ]

    stay = Stay(stay_id)
    stay.replay(events)

    assert stay.room_id == "101"
    assert stay.started_at == start
    assert stay.ended_at == end
    assert stay.version == 2
    assert stay.get_uncommitted_events() == []


# ============================================================
# event_from_record
# ============================================================

def test_event_from_record_all_types():
    stay_id = uuid4()
    ts = now()

    class FakeRecord:
        def __init__(self, event_type, payload):
            self.event_type = event_type
            self.payload = payload

    # CheckedIn
    record_in = FakeRecord(
        "StayCheckedIn",
        {
            "stay_id": str(stay_id),
            "room_id": "101",
            "started_at": ts.isoformat(),
        },
    )

    event = Stay.event_from_record(record_in)
    assert isinstance(event, StayCheckedIn)
    assert event.room_id == "101"

    # CheckedOut
    record_out = FakeRecord(
        "StayCheckedOut",
        {
            "stay_id": str(stay_id),
            "ended_at": ts.isoformat(),
        },
    )

    event = Stay.event_from_record(record_out)
    assert isinstance(event, StayCheckedOut)
    assert event.ended_at == ts

    # Relocated
    record_reloc = FakeRecord(
        "StayRelocated",
        {
            "stay_id": str(stay_id),
            "new_room_id": "202",
            "relocated_at": ts.isoformat(),
        },
    )

    event = Stay.event_from_record(record_reloc)
    assert isinstance(event, StayRelocated)
    assert event.new_room_id == "202"


def test_event_from_record_unknown_type_raises():
    class FakeRecord:
        event_type = "UnknownEvent"
        payload = {}

    with pytest.raises(ValueError):
        Stay.event_from_record(FakeRecord())