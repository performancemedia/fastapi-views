from __future__ import annotations

from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
    HTTP_429_TOO_MANY_REQUESTS,
)


class APIError(Exception):
    def __init__(
        self,
        detail: str,
        status: int = HTTP_400_BAD_REQUEST,
        title: str | None = None,
        instance: str | None = None,
    ):
        self.detail = detail
        self.status = status
        self.title = title or self.get_default_title(status)
        self.instance = instance

    @classmethod
    def get_default_title(cls, status_code: int) -> str:
        if cls != APIError:
            return cls.__name__

        if status_code >= 500:
            return "Internal Server Error"

        if status_code == 400:
            return "Bad Request"

        return "Something went wrong"


class NotFound(APIError):
    def __init__(self, detail: str, instance: str | None = None):
        super().__init__(
            detail, title="Not Found", status=HTTP_404_NOT_FOUND, instance=instance
        )


class Conflict(APIError):
    def __init__(self, detail: str, instance: str | None = None):
        super().__init__(
            detail, title="Conflict", status=HTTP_409_CONFLICT, instance=instance
        )


class Throttled(APIError):
    def __init__(self, detail: str, instance: str | None = None):
        super().__init__(
            detail,
            title="Too many requests",
            status=HTTP_429_TOO_MANY_REQUESTS,
            instance=instance,
        )


class Unauthorized(APIError):
    def __init__(self, detail: str, instance: str | None = None):
        super().__init__(
            detail,
            title="Unauthorized",
            status=HTTP_401_UNAUTHORIZED,
            instance=instance,
        )


class Forbidden(APIError):
    def __init__(self, detail: str, instance: str | None = None):
        super().__init__(
            detail, title="Forbidden", status=HTTP_403_FORBIDDEN, instance=instance
        )
