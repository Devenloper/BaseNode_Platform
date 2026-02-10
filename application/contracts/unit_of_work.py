from typing import Protocol
from application.contracts.aggregate_repository import AggregateRepository


class UnitOfWork(Protocol):
    repository: AggregateRepository

    async def __aenter__(self) -> "UnitOfWork":
        ...

    async def __aexit__(self, exc_type, exc, tb) -> None:
        ...

    async def rollback(self) -> None:
        ...