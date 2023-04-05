import os
from typing import Any

from fastapi import FastAPI


def add_prometheus_middleware(
    app: FastAPI, endpoint: str = "/metrics", **kwargs: Any
) -> None:
    from starlette_exporter import PrometheusMiddleware, handle_metrics

    kwargs.setdefault("app", app.title.lower().replace(" ", "_"))
    kwargs.setdefault("skip_paths", ["/healthz", "/docs", "/openapi.json", "/metrics"])
    kwargs.setdefault("group_paths", True)
    kwargs.setdefault("labels", {"server": os.getenv("HOSTNAME")})
    kwargs.setdefault("always_use_int_status", True)
    app.add_middleware(PrometheusMiddleware, **kwargs)
    app.add_route(endpoint, handle_metrics)
