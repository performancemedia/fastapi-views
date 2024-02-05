from __future__ import annotations

from collections.abc import Mapping
from functools import cached_property
from typing import Any, Callable, Generic, TypeVar, Union

from fastapi import Request
from pydantic import BaseModel
from starlette.status import HTTP_400_BAD_REQUEST

from ..errors.exceptions import APIError, NotFound
from ..schemas import IdSchema
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
        raise NotFound(f"{self.get_name()} does not exist.")


class _Sentinel(Exception):
    pass


class ErrorHandlerMixin:
    request: Request

    raises: dict[type[Exception], str | dict[str, Any]] = {}

    def get_error_message(self, key: type[Exception]) -> str | dict[str, Any]:
        return self.raises.get(key, {})

    def handle_error(self, exc: Exception, **kwargs):
        kw = self.get_error_message(type(exc))
        if isinstance(kw, str):
            kwargs["detail"] = kw
        elif isinstance(kw, Mapping):
            kwargs.update(kw)
        kwargs.setdefault("instance", self.request.url.path)
        kwargs.setdefault("title", type(exc).__name__)
        kwargs.setdefault("detail", str(exc))
        kwargs.setdefault("status", HTTP_400_BAD_REQUEST)
        raise APIError(**kwargs)

    def get_exception_class(self) -> tuple[type[Exception], ...] | type[Exception]:
        return tuple(self.raises.keys()) or _Sentinel


class GenericViewMixin(ErrorHandlerMixin, Generic[R]):
    repository_factory: Callable[..., R]
    params: type[BaseModel] = BaseModel

    @cached_property
    def repository(self) -> R:
        return self.repository_factory()

    @classmethod
    def get_params(cls, action: str):
        return cls.params


class GenericDetailViewMixin(GenericViewMixin[R], DetailViewMixin):
    pk: type[BaseModel] = IdSchema
