# application/exceptions.py


class InvalidExpectedVersionError(Exception):
    """Raised when expected_version is invalid (e.g., negative)."""
    pass


class VersionConflictError(Exception):
    """
    Raised when optimistic locking detects a version mismatch.

    Application-level exception.
    Infrastructure may raise it but does not own it.
    """

    def __init__(self, aggregate_id, expected: int, actual: int):
        self.aggregate_id = aggregate_id
        self.expected = expected
        self.actual = actual

        super().__init__(
            f"Version conflict for aggregate {aggregate_id}: "
            f"expected {expected}, actual {actual}"
        )