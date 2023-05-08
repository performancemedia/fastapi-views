import asyncio
from typing import Any, AsyncGenerator, Optional

import pytest
import pytest_asyncio
from asgi_lifespan import LifespanManager
from fastapi import FastAPI
from httpx import AsyncClient

from fastapi_views import Serializer, ViewRouter
from fastapi_views.views.api import (
    AsyncCreateAPIView,
    AsyncDestroyAPIView,
    AsyncListAPIView,
    AsyncRetrieveAPIView,
)
from fastapi_views.views.viewsets import AsyncGenericViewSet


@pytest_asyncio.fixture(scope="session")
def event_loop():
    return asyncio.get_event_loop()


@pytest.fixture()
def app():
    return FastAPI()


@pytest_asyncio.fixture(scope="session")
async def asgi_lifespan(app):
    async with LifespanManager(app, startup_timeout=30):
        yield


@pytest_asyncio.fixture(scope="function")
async def client(app) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://test") as test_client:
        yield test_client


class DummySerializer(Serializer):
    x: str = "test"


@pytest.fixture(scope="session")
def dummy_data():
    return {"x": "test"}


def view_as_fixture(name: str, prefix: str = "/test"):
    def wrapper(cls):
        @pytest.fixture(name=name)
        def _view_fixture(app: FastAPI):

            router = ViewRouter()
            router.register_view(cls, prefix=prefix)
            app.include_router(router)

        return _view_fixture

    return wrapper


@view_as_fixture("list_view")
class TestListView(AsyncListAPIView):
    serializer = DummySerializer

    async def list(self) -> Any:
        return [None]


@view_as_fixture("retrieve_view")
class TestRetrieveView(AsyncRetrieveAPIView):
    detail_route = ""
    serializer = DummySerializer

    async def retrieve(self) -> Optional[Any]:
        return DummySerializer(x="test")


@view_as_fixture("destroy_view")
class TestDestroyView(AsyncDestroyAPIView):
    detail_route = ""

    async def destroy(self) -> None:
        assert 1 == 1


@view_as_fixture("create_view")
class TestCreateView(AsyncCreateAPIView):
    serializer = DummySerializer

    async def create(self) -> Any:
        return DummySerializer(x="test")


class FakeRepository:
    async def retrieve(self, *args, **kwargs):
        return DummySerializer(x="test")

    async def create(self, *args, **kwargs):
        return DummySerializer(x="test")

    async def update(self, *args, **kwargs):
        return DummySerializer(x="test")

    async def partial_update(self, *args, **kwargs):
        return DummySerializer(x="test")

    async def delete(self, *args, **kwargs) -> None:
        pass

    async def list(self, *args, **kwargs):
        return [DummySerializer(x="test")]


@view_as_fixture("generic_viewset")
class TestGenericViewSet(AsyncGenericViewSet):
    repository = FakeRepository()
    serializer = DummySerializer
