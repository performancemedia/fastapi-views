from __future__ import annotations

from fastapi import FastAPI

from .errors import ServiceUnavailableAPIError, add_error_handlers
from .healthcheck import HealthCheck
from .openapi import simplify_operation_ids
from .prometheus import add_prometheus_middleware
from .settings import APISettings

try:
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

except ImportError:
    FastAPIInstrumentor = None


def configure_app(
    app: FastAPI,
    enable_error_handlers: bool = True,
    healthcheck: HealthCheck | None = None,
    enable_prometheus_middleware: bool = True,
    simplify_openapi_ids: bool = True,
    **tracing_opts,
):
    if enable_error_handlers:
        add_error_handlers(app)
    if healthcheck:
        app.add_api_route(
            methods=["GET"],
            path=healthcheck.endpoint,
            endpoint=healthcheck.get_endpoint,
            include_in_schema=healthcheck.include_in_schema,
            responses={503: {"model": ServiceUnavailableAPIError}},
        )
    if enable_prometheus_middleware:
        add_prometheus_middleware(app)
    if simplify_openapi_ids:
        simplify_operation_ids(app)

    if FastAPIInstrumentor is not None:
        FastAPIInstrumentor.instrument_app(app, **tracing_opts)


def create_fastapi_app(settings: APISettings, **kwargs) -> FastAPI:
    app = FastAPI(**settings.fastapi_kwargs, **kwargs)
    configure_app(app, **settings.config_kwargs)
    return app


def create_fastapi_from_env(**kwargs):
    settings = APISettings(**kwargs)
    return create_fastapi_app(settings)
