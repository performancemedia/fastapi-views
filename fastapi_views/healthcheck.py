from __future__ import annotations

import asyncio
import logging
from typing import Any, Callable

from starlette.status import HTTP_200_OK, HTTP_503_SERVICE_UNAVAILABLE

from .errors import ServiceUnavailableAPIError
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
        failed = False
        task = asyncio.gather(*[t() for t in self.checks], return_exceptions=True)
        try:
            results = await asyncio.wait_for(task, timeout=10)
            for r in results:
                if isinstance(r, Exception):
                    self.logger.warning(f"Healthcheck failed with exc: {r}")
                    failed = True
                    break
        except asyncio.TimeoutError:
            failed = True
        finally:
            if failed:
                return self.response_class(
                    content=ServiceUnavailableAPIError(
                        detail="Service liveness probe failed"
                    ).dict(),
                    status_code=HTTP_503_SERVICE_UNAVAILABLE,
                )
            return self.response_class(
                content={"status": "ok"}, status_code=HTTP_200_OK
            )
