from __future__ import annotations

from typing import Protocol, TypeVar

Entity = TypeVar("Entity")


class Repository(Protocol[Entity]):
    async def retrieve(self, *args, **kwargs) -> Entity | None:
        ...

    async def create(self, *args, **kwargs) -> Entity | None:
        ...

    async def update(self, *args, **kwargs) -> Entity | None:
        ...

    async def partial_update(self, *args, **kwargs) -> Entity | None:
        ...

    async def delete(self, *args, **kwargs) -> None:
        ...

    async def list(self, *args, **kwargs) -> list[Entity]:
        ...


class SideService(Protocol):
    async def start(self, *args, **kwargs) -> None:
        ...

    async def stop(self, *args, **kwargs) -> None:
        ...
