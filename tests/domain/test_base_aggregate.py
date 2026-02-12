import pytest
from uuid import uuid4

from domain.common.base_aggregate import BaseAggregate


# ============================================================
# Dummy setup
# ============================================================

class DummyEvent:
    pass


class DummyAggregate(BaseAggregate):

    def __init__(self, aggregate_id):
        super().__init__(aggregate_id)
        self.applied = False

    def _apply_DummyEvent(self, event):
        self.applied = True


# ============================================================
# Apply logic
# ============================================================

def test_apply_increments_version_and_calls_handler():
    agg = DummyAggregate(uuid4())

    event = DummyEvent()
    agg._apply(event)

    assert agg.version == 1
    assert agg.applied is True


def test_apply_without_handler_raises():
    agg = DummyAggregate(uuid4())

    class UnknownEvent:
        pass

    with pytest.raises(NotImplementedError):
        agg._apply(UnknownEvent())


# ============================================================
# Uncommitted lifecycle
# ============================================================

def test_add_and_clear_uncommitted_events():
    agg = DummyAggregate(uuid4())

    event = DummyEvent()

    agg._apply(event)
    agg._add_uncommitted_event(event)

    assert len(agg.get_uncommitted_events()) == 1

    agg.clear_uncommitted_events()

    assert agg.get_uncommitted_events() == []


# ============================================================
# Replay
# ============================================================

def test_replay_increments_version_and_clears_uncommitted():
    agg = DummyAggregate(uuid4())

    events = [DummyEvent(), DummyEvent()]

    agg.replay(events)

    assert agg.version == 2
    assert agg.get_uncommitted_events() == []


def test_replay_without_handler_raises():
    agg = DummyAggregate(uuid4())

    class UnknownEvent:
        pass

    with pytest.raises(NotImplementedError):
        agg.replay([UnknownEvent()])