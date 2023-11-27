from __future__ import annotations

from typing import Any, Literal, Protocol, TypeVar

Entity = TypeVar("Entity", bound=dict[str, Any])
Action = Literal["create", "list", "retrieve", "update", "destroy", "partial_update"]


class Repository(Protocol[Entity]):
    def retrieve(self, *args, **kwargs) -> Entity | None:
        ...

    def create(self, entity: Entity, **kwargs) -> Entity | None:
        ...

    def update(self, entity: Entity, **kwargs) -> Entity | None:
        ...

    def delete(self, *args, **kwargs) -> None:
        ...

    def list(self, *args, **kwargs) -> list[Entity]:
        ...


class AsyncRepository(Protocol[Entity]):
    async def retrieve(self, *args, **kwargs) -> Entity | None:
        ...

    async def create(self, entity: Entity, **kwargs) -> Entity | None:
        ...

    async def update(self, entity: Entity, **kwargs) -> Entity | None:
        ...

    async def delete(self, *args, **kwargs) -> None:
        ...

    async def list(self, *args, **kwargs) -> list[Entity]:
        ...
