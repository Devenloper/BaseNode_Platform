from typing import Protocol, Type, TypeVar
from uuid import UUID

T = TypeVar("T")


class AggregateRepository(Protocol):

    async def load(self, aggregate_cls: Type[T], aggregate_id: UUID) -> T:
        """
        Должен вернуть пустой агрегат (version=0),
        если событий нет.
        """

    async def save(
        self,
        aggregate: T,
        *,
        expected_version: int,
        metadata: dict,
    ) -> None:
        """
        expected_version обязателен.
        Версия не вычисляется внутри Application.
        """