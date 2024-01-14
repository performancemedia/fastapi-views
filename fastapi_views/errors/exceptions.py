from __future__ import annotations

from .models import (
    BadRequestErrorDetails,
    ConflictErrorDetails,
    ErrorDetails,
    ForbiddenErrorDetails,
    NotFoundErrorDetails,
    ServiceUnavailableErrorDetails,
    TooManyRequestsErrorDetails,
    UnauthorizedErrorDetails,
    UnprocessableEntityErrorDetails,
)


class APIError(Exception):
    model: type[ErrorDetails] = ErrorDetails

    def __init__(self, detail: str, headers: dict[str, str] | None = None, **kwargs):
        self.detail = detail
        self.headers = headers
        self.kwargs = kwargs

    def get_status(self) -> int:
        return self.model.model_fields["status"].get_default()

    def as_model(self, **kwargs) -> ErrorDetails:
        return self.model(detail=self.detail, **self.kwargs, **kwargs)


class NotFound(APIError):
    model = NotFoundErrorDetails


class UnprocessableEntity(APIError):
    model = UnprocessableEntityErrorDetails


class BadRequest(APIError):
    model = BadRequestErrorDetails


class Conflict(APIError):
    model = ConflictErrorDetails


class Throttled(APIError):
    model = TooManyRequestsErrorDetails


class Unauthorized(APIError):
    model = UnauthorizedErrorDetails


class Forbidden(APIError):
    model = ForbiddenErrorDetails


class Unavailable(APIError):
    model = ServiceUnavailableErrorDetails
