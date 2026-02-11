import pytest
from uuid import uuid4

from domain.common.base_aggregate import BaseAggregate, DomainError


# ============================================================
# Test aggregate implementation
# ============================================================

class DummyEvent:
    pass


class DummyAggregate(BaseAggregate):

    def __init__(self, aggregate_id):
        super().__init__(aggregate_id)
        self.applied = False
        self._handlers = {
            DummyEvent: self._apply_dummy
        }

    def _apply_dummy(self, event):
        self.applied = True


# ============================================================
# Tests
# ============================================================

def test_replay_increments_version():
    agg = DummyAggregate(uuid4())

    events = [DummyEvent(), DummyEvent(), DummyEvent()]

    agg.replay(events)

    assert agg.version == 3


def test_handler_not_found_raises_domain_error():
    agg = DummyAggregate(uuid4())

    class UnknownEvent:
        pass

    with pytest.raises(DomainError):
        agg.apply(UnknownEvent())


def test_clear_uncommitted_events():
    agg = DummyAggregate(uuid4())

    agg._record_event(DummyEvent())
    agg._record_event(DummyEvent())

    assert len(agg.get_uncommitted_events()) == 2

    agg.clear_uncommitted_events()

    assert agg.get_uncommitted_events() == []


def test_version_increases_only_via_apply():
    agg = DummyAggregate(uuid4())

    assert agg.version == 0

    agg._record_event(DummyEvent())
    assert agg.version == 1

    # прямое изменение запрещено — проверяем,
    # что version меняется только через apply
    previous_version = agg.version
    agg._uncommitted_events.append(DummyEvent())

    assert agg.version == previous_version