from __future__ import annotations

import logging
from typing import Any, Callable

from starlette.status import HTTP_200_OK, HTTP_503_SERVICE_UNAVAILABLE

from .errors.models import ServiceUnavailableErrorDetails
from .response import JsonResponse


async def _simple_healthcheck() -> bool:
    return True


class HealthCheck:
    """
    Group of functions that perform basic health checks of the application
    """

    def __init__(
        self,
        endpoint: str = "/healthz",
        checks: list[Callable[[], Any]] | None = None,
        response_class=JsonResponse,
        include_in_schema: bool = False,
    ):
        self.endpoint = endpoint
        self.response_class = response_class
        self.checks = checks or [_simple_healthcheck]
        self.include_in_schema = include_in_schema
        self.logger = logging.getLogger(type(self).__name__)

    def add_check(self, func):
        self.checks.append(func)

    def register(self):
        def wrapper(func):
            self.add_check(func)
            return func

        return wrapper

    async def get_endpoint(self):
        try:
            for check in self.checks:
                await check()
            return JsonResponse(content={"status": "ok"}, status_code=HTTP_200_OK)
        except Exception as e:
            self.logger.warning("Healthcheck failed with exception", exc_info=e)
            return self.response_class(
                content=ServiceUnavailableErrorDetails(
                    detail="Service liveness probe failed"
                ).model_dump_json(),
                status_code=HTTP_503_SERVICE_UNAVAILABLE,
            )
