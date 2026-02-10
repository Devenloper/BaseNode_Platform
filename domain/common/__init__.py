def __init__(self, stay_id: UUID):
    super().__init__(stay_id)

    self.lifecycle = StayLifecycle.NOT_STARTED

    self.room_id: UUID | None = None
    self.started_at: datetime | None = None
    self.ended_at: datetime | None = None

    self.conflict_detected: bool = False

    self._handlers = {
        StayCheckedIn: self._apply_checked_in,
        StayCheckedOut: self._apply_checked_out,
        StayRelocated: self._apply_relocated,
        StayConflictDetected: self._apply_conflict_detected,
    }