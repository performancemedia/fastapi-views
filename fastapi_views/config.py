from __future__ import annotations

import asyncio
from typing import Sequence

from fastapi import FastAPI

from .errors import ServiceUnavailableAPIError, add_error_handlers
from .healthcheck import HealthCheck
from .openapi import simplify_operation_ids
from .prometheus import add_prometheus_middleware
from .settings import APISettings
from .types import SideService


def add_side_services(app: FastAPI, services: Sequence[SideService]) -> None:
    @app.on_event("startup")
    async def start_side_services():
        await asyncio.gather(*[s.start() for s in services])

    @app.on_event("shutdown")
    async def stop_side_services():
        await asyncio.gather(*[s.stop() for s in services])


def configure_app(
    app: FastAPI,
    enable_error_handlers: bool = True,
    healthcheck: HealthCheck | None = None,
    enable_prometheus_middleware: bool = True,
    side_services: Sequence[SideService] | None = None,
    simplify_openapi_ids: bool = True,
):
    if enable_error_handlers:
        add_error_handlers(app)
    if healthcheck:
        app.add_api_route(
            methods=["GET"],
            path=healthcheck.endpoint,
            endpoint=healthcheck.get_endpoint,
            responses={503: {"model": ServiceUnavailableAPIError}},
        )
    if enable_prometheus_middleware:
        add_prometheus_middleware(app)
    if side_services:
        add_side_services(app, side_services)
    if simplify_openapi_ids:
        simplify_operation_ids(app)


def create_fastapi_app(settings: APISettings, **kwargs) -> FastAPI:
    app = FastAPI(**settings.fastapi_kwargs, **kwargs)
    configure_app(app, **settings.config_kwargs)
    return app


def create_fastapi_from_env(**kwargs):
    settings = APISettings(**kwargs)
    return create_fastapi_app(settings)
