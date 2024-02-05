## Basic views


```python
from fastapi_views.views import get, post
from fastapi_views.views.api import View

class CustomView(View):
    
    @get("")
    async def list_come_items(self):
        ...
    
    @post("")
    async def add_item(self):
        ...

```

## ApiView

```python
from pydantic import BaseModel
from fastapi_views.views.functools import get, post
from fastapi_views.views.api import APIView

class ItemSerializer(BaseModel):
    id: int
    name: str
    price: int

class CustomView(APIView):
    response_schema = ItemSerializer 

    @get("")
    async def list_come_items(self) -> list[ItemSerializer]:
        ...
    
    @post("")
    async def add_item(self, item: ItemSerializer) -> ItemSerializer:
        ...

```

## Generics

```python
from fastapi_views.views.generics import GenericListView

class MyGenericView(GenericListView):
    response_schema = ...
    repository = ... # <- set your own interface provider

```

## Viewsets

```python
from typing import Optional
from uuid import UUID
from pydantic import BaseModel
from fastapi_views.views.viewsets import AsyncAPIViewSet


class ItemSchema(BaseModel):
    id: UUID
    name: str
    price: int


items = {}


class MyViewSet(AsyncAPIViewSet):
    api_component_name = "Item"
    response_schema = ItemSchema
    
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

```