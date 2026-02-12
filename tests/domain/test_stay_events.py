import pytest
from uuid import uuid4
from datetime import datetime, timezone

from domain.stay.events import (
    StayCheckedIn,
    StayCheckedOut,
    StayRelocated,
)


def now():
    return datetime.now(timezone.utc)


# ============================================================
# StayCheckedIn
# ============================================================

def test_stay_checked_in_to_dict():
    stay_id = uuid4()
    started_at = now()

    event = StayCheckedIn(
        stay_id=stay_id,
        room_id="101",
        started_at=started_at,
    )

    data = event.to_dict()

    assert data["stay_id"] == str(stay_id)
    assert data["room_id"] == "101"
    assert data["started_at"] == started_at.isoformat()


def test_stay_checked_in_is_immutable():
    event = StayCheckedIn(
        stay_id=uuid4(),
        room_id="101",
        started_at=now(),
    )

    with pytest.raises(Exception):
        event.room_id = "999"


# ============================================================
# StayCheckedOut
# ============================================================

def test_stay_checked_out_to_dict():
    stay_id = uuid4()
    ended_at = now()

    event = StayCheckedOut(
        stay_id=stay_id,
        ended_at=ended_at,
    )

    data = event.to_dict()

    assert data["stay_id"] == str(stay_id)
    assert data["ended_at"] == ended_at.isoformat()


def test_stay_checked_out_is_immutable():
    event = StayCheckedOut(
        stay_id=uuid4(),
        ended_at=now(),
    )

    with pytest.raises(Exception):
        event.ended_at = now()


# ============================================================
# StayRelocated
# ============================================================

def test_stay_relocated_to_dict():
    stay_id = uuid4()
    relocated_at = now()

    event = StayRelocated(
        stay_id=stay_id,
        new_room_id="202",
        relocated_at=relocated_at,
    )

    data = event.to_dict()

    assert data["stay_id"] == str(stay_id)
    assert data["new_room_id"] == "202"
    assert data["relocated_at"] == relocated_at.isoformat()


def test_stay_relocated_is_immutable():
    event = StayRelocated(
        stay_id=uuid4(),
        new_room_id="202",
        relocated_at=now(),
    )

    with pytest.raises(Exception):
        event.new_room_id = "303"