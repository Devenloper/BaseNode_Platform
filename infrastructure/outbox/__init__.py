# infrastructure/outbox/__init__.py

"""
Outbox infrastructure package.
"""

# Correct location of OutboxRecord
from infrastructure.db.models import OutboxRecord

__all__ = [
    "OutboxRecord",
]