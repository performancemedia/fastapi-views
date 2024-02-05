from __future__ import annotations

import asyncio
import functools
from typing import TYPE_CHECKING, Any, Callable

from typing_extensions import ParamSpec

from fastapi_views.errors.exceptions import APIError

if TYPE_CHECKING:
    from fastapi_views.views.mixins import ErrorHandlerMixin

VIEWSET_ROUTE_FLAG = "_is_viewset_route"

P = ParamSpec("P")

F = Callable[[P.args, P.kwargs], Any]


def annotate(**kwargs: Any) -> Callable[[F], F]:
    def wrapper(func: F) -> F:
        func.kwargs = kwargs  # type: ignore[attr-defined]
        return func

    return wrapper


override = annotate


def errors(*exceptions: type[APIError]):
    return {e.model.get_status(): {"model": e.model} for e in exceptions}


def throws(*exceptions: type[APIError]):
    return override(responses=errors(*exceptions))


def route(path: str, **kwargs: Any) -> Callable[[F], F]:
    def wrapper(func: F) -> F:
        setattr(func, VIEWSET_ROUTE_FLAG, True)
        return override(path=path, **kwargs)(func)

    return wrapper


def catch(exc_type: type[Exception] | tuple[type[Exception]], **kw: Any):
    def wrapper(func):
        @functools.wraps(func)
        async def wrapped_async(self: ErrorHandlerMixin, *args, **kwargs):
            try:
                return await func(self, *args, **kwargs)
            except exc_type as e:
                self.handle_error(e, **kw)

        @functools.wraps(func)
        def wrapped_sync(self: ErrorHandlerMixin, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except exc_type as e:
                self.handle_error(e, **kw)

        if asyncio.iscoroutinefunction(func):
            return wrapped_async
        return wrapped_sync

    return wrapper


def catch_defined(func):
    @functools.wraps(func)
    async def wrapped_async(self: ErrorHandlerMixin, *args, **kwargs):
        try:
            return await func(self, *args, **kwargs)
        except self.get_exception_class() as e:
            self.handle_error(e)

    @functools.wraps(func)
    def wrapped_sync(self: ErrorHandlerMixin, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except self.get_exception_class() as e:
            self.handle_error(e)

    if asyncio.iscoroutinefunction(func):
        return wrapped_async
    return wrapped_sync


get = functools.partial(route, methods=["GET"])
post = functools.partial(route, methods=["POST"])
put = functools.partial(route, methods=["PUT"])
patch = functools.partial(route, methods=["PATCH"])
delete = functools.partial(route, methods=["DELETE"])
