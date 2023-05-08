import random
from typing import Optional, Type, TypeVar
from uuid import UUID

from fastapi import FastAPI
from pydantic import BaseModel

from fastapi_views import Serializer, ViewRouter, configure_app
from fastapi_views.healthcheck import HealthCheck
from fastapi_views.views.viewsets import AsyncAPIViewSet


class ItemSchema(Serializer):
    id: UUID
    name: str
    price: int


items: dict[UUID, ItemSchema] = {}

P = TypeVar("P", bound=Type[BaseModel])


class MyViewSet(AsyncAPIViewSet):
    api_component_name = "Item"
    serializer = ItemSchema

    async def list(self):
        return list(items.values())

    async def create(self, item: ItemSchema) -> ItemSchema:
        items[item.id] = item
        return item

    async def retrieve(self, id: UUID) -> Optional[ItemSchema]:
        return items.get(id)

    async def update(self, item: ItemSchema):
        items[item.id] = item

    async def destroy(self, id: UUID) -> None:
        items.pop(id, None)


async def healthcheck():
    if random.randint(1, 5) == 3:  # nosec
        raise Exception("Something went wrong")


hc = HealthCheck(checks=[healthcheck])

router = ViewRouter(prefix="/items")
router.register_view(MyViewSet)

app = FastAPI(title="My API")
app.include_router(router)

configure_app(app, healthcheck=hc)
