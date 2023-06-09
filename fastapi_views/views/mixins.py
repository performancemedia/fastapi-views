from __future__ import annotations

from typing import Any, Callable, Generic, TypeVar, Union
from uuid import UUID

from fastapi import Request
from pydantic import BaseModel
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND

from ..errors import APIError
from ..types import AsyncRepository, Repository

R = TypeVar("R", bound=Union[AsyncRepository, Repository])


class DetailViewMixin:
    detail_route: str = "/{id}"
    raise_on_none: bool = True
    request: Request
    get_name: Callable[..., str]

    @classmethod
    def get_detail_route(cls, action: str):
        return cls.detail_route

    def raise_not_found_error(self):
        raise APIError(f"{self.get_name()} does not exist.", status=HTTP_404_NOT_FOUND)


class _Sentinel(Exception):
    pass


class ErrorHandlerMixin:
    request: Request

    catch: dict[type[Exception], dict[str, Any]] = {}

    def get_error_message(self, key: type[Exception]):
        return self.catch.get(
            key, {"detail": "Something went wrong", "status": HTTP_400_BAD_REQUEST}
        )

    def handle_error(self, exc_type: type[Exception], exc: Exception, **kwargs):
        kwargs.update(**self.get_error_message(exc_type))
        kwargs.setdefault("instance", self.request.url.path)
        kwargs.setdefault("title", exc_type.__name__)
        kwargs.setdefault("detail", str(exc))
        raise APIError(**kwargs)

    @property
    def catches(self):
        return tuple(self.catch.keys()) or _Sentinel


class IdModel(BaseModel):
    id: UUID


class GenericViewMixin(ErrorHandlerMixin, Generic[R]):
    repository: R
    params: type[BaseModel] = BaseModel

    @classmethod
    def get_params(cls, action: str):
        return cls.params


class GenericDetailViewMixin(GenericViewMixin[R], DetailViewMixin):
    pk: type[BaseModel] = IdModel
