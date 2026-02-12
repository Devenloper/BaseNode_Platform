class VersionConflictError(Exception):
    def __init__(self, aggregate_id, expected, actual):
        self.aggregate_id = aggregate_id
        self.expected = expected
        self.actual = actual
        super().__init__(
            f"Version conflict for {aggregate_id}: "
            f"expected={expected}, actual={actual}"
        )