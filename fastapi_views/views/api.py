import asyncio
import inspect
from abc import ABC, abstractmethod
from collections.abc import Awaitable, Generator, Iterator
from typing import TYPE_CHECKING, Any, Callable, Generic, Optional, TypeVar, Union

from fastapi import Depends, Request, Response
from starlette.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_404_NOT_FOUND,
    HTTP_422_UNPROCESSABLE_ENTITY,
)

from ..errors import errors
from ..models import Serializer
from ..response import JsonResponse
from .functools import VIEWSET_ROUTE_FLAG
from .mixins import DetailViewMixin, ErrorHandlerMixin

S = TypeVar("S", bound=type[Serializer])
P = Iterator[dict[str, Any]]

Endpoint = Callable[..., Union[Response, Awaitable[Response]]]


class View(ABC):
    """
    Basic View Class
    Usage:
    from fastapi_views.views.functools import get, post, delete

    class MyCustomViewClass(View):

        @get("")
        async def get_items(self, ...):
            ...

        @post(path="")
    """

    api_component_name: str
    default_response_class: type[Response] = JsonResponse

    def __init__(self, request: Request, response: Response) -> None:
        self.request = request
        self.response = response

    @classmethod
    def get_name(cls) -> str:
        return getattr(cls, "api_component_name", cls.__name__)

    @classmethod
    def get_slug_name(cls) -> str:
        return f"{cls.get_name().lower().replace(' ', '_')}"

    @classmethod
    def get_api_actions(cls, prefix: str = ""):
        yield from cls.get_custom_api_actions(prefix)

    @classmethod
    def get_custom_endpoint(cls, func):
        # TODO: verify if those functions need to be redefined in loop
        async def _async_endpoint(self, *args, **kwargs):
            res = await func(self, *args, **kwargs)
            return self.get_response(content=res)

        def _sync_endpoint(self, *args, **kwargs):
            res = func(self, *args, **kwargs)
            return self.get_response(content=res)

        if asyncio.iscoroutinefunction(func):
            endpoint = _async_endpoint
        else:
            endpoint = _sync_endpoint

        cls._patch_endpoint_signature(endpoint, func)
        return endpoint

    @classmethod
    def get_custom_api_actions(cls, prefix: str = ""):
        for _, route_endpoint in inspect.getmembers(
            cls, lambda member: callable(member) and hasattr(member, VIEWSET_ROUTE_FLAG)
        ):
            endpoint = cls.get_custom_endpoint(route_endpoint)
            yield cls.get_api_action(
                endpoint, prefix=prefix, name=f"{endpoint.__name__} {cls.get_name()}"
            )

    @classmethod
    def get_api_action(
        cls, endpoint: Callable, prefix: str = "", path: str = "", **kwargs
    ) -> dict[str, Any]:
        kw = getattr(endpoint, "kwargs", {})
        kwargs.update(kw)
        path = kwargs.get("path", path)
        kwargs["endpoint"] = endpoint
        kwargs["path"] = prefix + path
        kwargs.setdefault("name", endpoint.__name__)
        endpoint_name = kwargs["name"]
        kwargs.setdefault("methods", ["GET"])
        # kwargs.setdefault("response_model", get_type_hints(endpoint).get("return"))
        kwargs.setdefault("operation_id", f"{cls.get_slug_name()}_{endpoint_name}")

        return kwargs

    @classmethod
    def _patch_metadata(cls, endpoint, method: Callable) -> None:
        setattr(endpoint, "__doc__", method.__doc__)
        setattr(endpoint, "__name__", method.__name__)
        setattr(endpoint, "kwargs", getattr(method, "kwargs", {}))

    @classmethod
    def _patch_endpoint_signature(cls, endpoint, method: Callable) -> None:
        old_signature = inspect.signature(method)
        old_parameters: list[inspect.Parameter] = list(
            old_signature.parameters.values()
        )
        old_first_parameter = old_parameters[0]
        new_first_parameter = old_first_parameter.replace(default=Depends(cls))
        new_parameters = [new_first_parameter] + [
            parameter.replace(kind=inspect.Parameter.KEYWORD_ONLY)
            for parameter in old_parameters[1:]
        ]
        new_signature = old_signature.replace(parameters=new_parameters)
        setattr(endpoint, "__signature__", new_signature)
        cls._patch_metadata(endpoint, method)

    def get_response(self, content: Any) -> Response:
        if isinstance(content, Response):
            return content
        return self.default_response_class(
            content=content,
            status_code=self.response.status_code or HTTP_200_OK,
            headers=dict(self.response.headers),
        )


class APIView(View, ErrorHandlerMixin, Generic[S]):
    """
    View with build-in json serialization via
    `serializer` and error handling
    """

    serializer: S

    @classmethod
    def get_serializer(cls, action: str) -> S:
        return cls.serializer

    def serialize_response(
        self, action: str, content: Any, status_code: int = HTTP_200_OK
    ):
        if content:
            serializer = self.get_serializer(action)
            content = serializer.parse(content)
        if self.response.status_code is None:
            self.response.status_code = status_code
        return self.get_response(content)


class BaseListAPIView(APIView):
    serializer_to_list: bool = True

    @classmethod
    @abstractmethod
    def get_list_endpoint(cls) -> Endpoint:
        raise NotImplementedError

    @classmethod
    def get_api_actions(cls, prefix: str = ""):
        response_model = (
            list[cls.get_serializer("list")]  # type: ignore
            if cls.serializer_to_list
            else cls.get_serializer("list")
        )
        yield cls.get_api_action(
            prefix=prefix,
            endpoint=cls.get_list_endpoint(),
            methods=["GET"],
            response_model=response_model,
            name=f"List {cls.get_name()}",
            operation_id=f"list_{cls.get_slug_name()}",
        )
        yield from super().get_api_actions(prefix)


class AsyncListAPIView(BaseListAPIView, ABC):
    """Async list api view"""

    @classmethod
    def get_list_endpoint(cls) -> Endpoint:
        async def endpoint(self: AsyncListAPIView, *args, **kwargs):
            objects = await self.list(*args, **kwargs)
            return self.serialize_response("list", objects)

        cls._patch_endpoint_signature(endpoint, cls.list)
        return endpoint

    if TYPE_CHECKING:
        list: Callable[..., Awaitable[Any]]
    else:

        @abstractmethod
        async def list(self, *args, **kwargs) -> Any:
            raise NotImplementedError


class ListAPIView(BaseListAPIView, ABC):
    """Sync list api view"""

    @classmethod
    def get_list_endpoint(cls) -> Endpoint:
        def endpoint(self: ListAPIView, *args, **kwargs):
            objects = self.list(*args, **kwargs)
            return self.serialize_response("list", objects)

        cls._patch_endpoint_signature(endpoint, cls.list)
        return endpoint

    if TYPE_CHECKING:
        list: Callable[..., Any]

    else:

        @abstractmethod
        def list(self, *args, **kwargs) -> Any:
            raise NotImplementedError


class BaseRetrieveAPIView(APIView, DetailViewMixin):
    @classmethod
    @abstractmethod
    def get_retrieve_endpoint(cls) -> Endpoint:
        raise NotImplementedError

    @classmethod
    def get_api_actions(cls, prefix: str = ""):
        yield cls.get_api_action(
            prefix=prefix,
            endpoint=cls.get_retrieve_endpoint(),
            path=cls.get_detail_route(action="retrieve"),
            methods=["GET"],
            responses=errors(404),
            response_model=cls.get_serializer(action="retrieve"),
            name=f"Get {cls.get_name()}",
            operation_id=f"get_{cls.get_slug_name()}",
        )
        yield from super().get_api_actions(prefix)


class RetrieveAPIView(BaseRetrieveAPIView):
    """Sync retrieve api view"""

    @classmethod
    def get_retrieve_endpoint(cls) -> Endpoint:
        def endpoint(self: RetrieveAPIView, *args, **kwargs):
            obj = self.retrieve(*args, **kwargs)
            if obj is None and self.raise_on_none:
                self.raise_not_found_error()
            return self.serialize_response("retrieve", obj)

        cls._patch_endpoint_signature(endpoint, cls.retrieve)
        return endpoint

    if TYPE_CHECKING:
        retrieve: Callable[..., Optional[Any]]
    else:

        @abstractmethod
        def retrieve(self, *args, **kwargs) -> Optional[Any]:
            raise NotImplementedError


class AsyncRetrieveAPIView(BaseRetrieveAPIView):
    """Async retrieve api view"""

    @classmethod
    def get_retrieve_endpoint(cls) -> Endpoint:
        async def endpoint(self: AsyncRetrieveAPIView, *args, **kwargs):
            obj = await self.retrieve(*args, **kwargs)
            if obj is None and self.raise_on_none:
                self.raise_not_found_error()
            return self.serialize_response("retrieve", obj)

        cls._patch_endpoint_signature(endpoint, cls.retrieve)
        return endpoint

    if TYPE_CHECKING:
        retrieve: Callable[..., Awaitable[Any]]
    else:

        @abstractmethod
        async def retrieve(self, *args, **kwargs) -> Optional[Any]:
            raise NotImplementedError


class BaseCreateAPIView(APIView):
    return_on_create: bool = True

    @classmethod
    @abstractmethod
    def get_create_endpoint(cls) -> Endpoint:
        raise NotImplementedError

    @classmethod
    def get_api_actions(cls, prefix: str = ""):
        yield cls.get_api_action(
            prefix=prefix,
            endpoint=cls.get_create_endpoint(),
            methods=["POST"],
            status_code=201,
            responses=errors(409, 422),
            response_model=cls.get_serializer(action="create"),
            name=f"Create {cls.get_name()}",
            operation_id=f"create_{cls.get_slug_name()}",
        )
        yield from super().get_api_actions(prefix)


class CreateAPIView(BaseCreateAPIView):
    """Sync create api view"""

    @classmethod
    def get_create_endpoint(cls) -> Endpoint:
        def endpoint(self: CreateAPIView, *args, **kwargs):
            obj = self.create(*args, **kwargs)
            if self.return_on_create:
                return self.serialize_response("create", obj, HTTP_201_CREATED)
            return Response(status_code=HTTP_201_CREATED)

        cls._patch_endpoint_signature(endpoint, cls.create)
        return endpoint

    if TYPE_CHECKING:
        create: Callable[..., Any]

    else:

        @abstractmethod
        def create(self, *args, **kwargs) -> Any:
            raise NotImplementedError


class AsyncCreateAPIView(BaseCreateAPIView):
    """Async create api view"""

    @classmethod
    def get_create_endpoint(cls) -> Endpoint:
        async def endpoint(self: AsyncCreateAPIView, *args, **kwargs):
            obj = await self.create(*args, **kwargs)
            if self.return_on_create:
                return self.serialize_response("create", obj, HTTP_201_CREATED)
            return Response(status_code=HTTP_201_CREATED)

        cls._patch_endpoint_signature(endpoint, cls.create)
        return endpoint

    if TYPE_CHECKING:
        create: Callable[..., Awaitable[Any]]

    else:

        @abstractmethod
        async def create(self, *args, **kwargs) -> Any:
            raise NotImplementedError


class BaseUpdateAPIView(APIView, DetailViewMixin):
    return_on_update: bool = True

    @classmethod
    @abstractmethod
    def get_update_endpoint(cls) -> Endpoint:
        raise NotImplementedError

    @classmethod
    def get_api_actions(cls, prefix: str = ""):

        yield cls.get_api_action(
            prefix=prefix,
            path=cls.get_detail_route(action="update"),
            endpoint=cls.get_update_endpoint(),
            methods=["PUT"],
            responses=errors(HTTP_404_NOT_FOUND, HTTP_422_UNPROCESSABLE_ENTITY),
            response_model=cls.get_serializer(action="update"),
            name=f"Update {cls.get_name()}",
            operation_id=f"update_{cls.get_slug_name()}",
        )
        yield from super().get_api_actions(prefix)


class UpdateAPIView(BaseUpdateAPIView):
    """Sync update api view"""

    @classmethod
    def get_update_endpoint(cls) -> Endpoint:
        def endpoint(self, *args, **kwargs):
            obj = self.update(*args, **kwargs)
            if not self.return_on_update:
                return Response(status_code=HTTP_200_OK)
            if obj is None and self.raise_on_none:
                self.raise_not_found_error()
            return self.serialize_response("update", obj)

        cls._patch_endpoint_signature(endpoint, cls.update)
        return endpoint

    if TYPE_CHECKING:
        update: Callable[..., Any]

    else:

        @abstractmethod
        def update(self, *args, **kwargs):
            raise NotImplementedError


class AsyncUpdateAPIView(BaseUpdateAPIView):
    """Async update api view"""

    @classmethod
    def get_update_endpoint(cls) -> Endpoint:
        async def endpoint(self, *args, **kwargs):
            obj = await self.update(*args, **kwargs)
            if not self.return_on_update:
                return Response(status_code=HTTP_200_OK)
            if obj is None and self.raise_on_none:
                self.raise_not_found_error()
            return self.serialize_response("update", obj)

        cls._patch_endpoint_signature(endpoint, cls.update)
        return endpoint

    if TYPE_CHECKING:
        update: Callable[..., Awaitable[Any]]

    else:

        @abstractmethod
        async def update(self, *args, **kwargs):
            raise NotImplementedError


class BasePartialUpdateAPIView(APIView, DetailViewMixin):
    return_on_update: bool = True

    @classmethod
    def get_api_actions(cls, prefix: str = "") -> Generator:
        yield cls.get_api_action(
            prefix=prefix,
            path=cls.get_detail_route(action="update"),
            endpoint=cls.get_partial_update_endpoint(),
            methods=["PATCH"],
            responses=errors(HTTP_404_NOT_FOUND, HTTP_422_UNPROCESSABLE_ENTITY),
            response_model=cls.get_serializer(action="update"),
            name=f"Partial update {cls.get_name()}",
            operation_id=f"patch_{cls.get_slug_name()}",
        )

        yield from super().get_api_actions(prefix)

    @classmethod
    @abstractmethod
    def get_partial_update_endpoint(cls) -> Endpoint:
        raise NotImplementedError


class PartialUpdateAPIView(BasePartialUpdateAPIView):
    """Sync partial update api view"""

    @classmethod
    def get_partial_update_endpoint(cls) -> Endpoint:
        def endpoint(self, *args, **kwargs):
            obj = self.partial_update(*args, **kwargs)
            if obj is None and self.raise_on_none:
                self.raise_not_found_error()
            if self.return_on_update:
                return self.serialize_response("partial_update", obj)
            return Response(status_code=HTTP_200_OK)

        cls._patch_endpoint_signature(endpoint, cls.partial_update)
        return endpoint

    if TYPE_CHECKING:
        partial_update: Callable[..., Any]
    else:

        @abstractmethod
        def partial_update(self, *args, **kwargs):
            raise NotImplementedError


class AsyncPartialUpdateAPIView(BasePartialUpdateAPIView):
    """Async partial update api view"""

    @classmethod
    def get_partial_update_endpoint(cls) -> Endpoint:
        async def endpoint(self, *args, **kwargs):
            obj = await self.partial_update(*args, **kwargs)
            if obj is None and self.raise_on_none:
                self.raise_not_found_error()
            if self.return_on_update:
                return self.serialize_response("partial_update", obj)
            return Response(status_code=HTTP_200_OK)

        cls._patch_endpoint_signature(endpoint, cls.partial_update)
        return endpoint

    if TYPE_CHECKING:
        partial_update: Callable[..., Awaitable[Any]]
    else:

        @abstractmethod
        async def partial_update(self, *args, **kwargs):
            raise NotImplementedError


class BaseDestroyAPIView(APIView, DetailViewMixin):
    @classmethod
    def get_api_actions(cls, prefix: str = "") -> Generator:
        yield cls.get_api_action(
            prefix=prefix,
            path=cls.get_detail_route(action="destroy"),
            endpoint=cls.get_destroy_endpoint(),
            methods=["DELETE"],
            response_class=Response,
            status_code=HTTP_204_NO_CONTENT,
            name=f"Delete {cls.get_name()}",
            operation_id=f"delete_{cls.get_slug_name()}",
        )
        yield from super().get_api_actions(prefix)

    @classmethod
    @abstractmethod
    def get_destroy_endpoint(cls):
        raise NotImplementedError


class DestroyAPIView(BaseDestroyAPIView):
    """Sync destroy api view"""

    @classmethod
    def get_destroy_endpoint(cls) -> Endpoint:
        def endpoint(self, *args, **kwargs):
            self.destroy(*args, **kwargs)
            return Response(status_code=HTTP_204_NO_CONTENT)

        cls._patch_endpoint_signature(endpoint, cls.destroy)
        return endpoint

    if TYPE_CHECKING:
        destroy: Callable[..., None]
    else:

        @abstractmethod
        def destroy(self, *args, **kwargs) -> None:
            raise NotImplementedError


class AsyncDestroyAPIView(BaseDestroyAPIView):
    """Async destroy api view"""

    @classmethod
    def get_destroy_endpoint(cls) -> Endpoint:
        async def endpoint(self, *args, **kwargs):
            await self.destroy(*args, **kwargs)
            return Response(status_code=HTTP_204_NO_CONTENT)

        cls._patch_endpoint_signature(endpoint, cls.destroy)
        return endpoint

    if TYPE_CHECKING:
        destroy: Callable[..., Awaitable[None]]
    else:

        @abstractmethod
        async def destroy(self, *args, **kwargs) -> None:
            raise NotImplementedError
