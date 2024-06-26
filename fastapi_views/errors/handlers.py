from logging import getLogger

from fastapi import Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

from ..response import JsonResponse
from .exceptions import APIError
from .models import InternalServerErrorDetails, UnprocessableEntityErrorDetails

logger = getLogger("exceptions.handler")


def api_error_handler(request: Request, exc: APIError):
    model = exc.as_model()
    if model.instance is None:
        model.instance = request.url.path
    return JsonResponse(
        status_code=model.status,
        content=model.model_dump_json(),
        headers=exc.headers,
    )


def request_validation_handler(request: Request, exc: RequestValidationError):
    model = UnprocessableEntityErrorDetails(
        detail="Validation error",
        instance=request.url.path,
        errors=jsonable_encoder(exc.errors()),
    )
    return JsonResponse(
        status_code=model.status,
        content=model.model_dump_json(),
    )


def exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception", exc_info=exc)
    return JsonResponse(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        content=InternalServerErrorDetails(
            detail="Unhandled server error",
            instance=request.url.path,
        ).model_dump_json(),
    )


def add_error_handlers(app):
    app.add_exception_handler(APIError, api_error_handler)
    app.add_exception_handler(RequestValidationError, request_validation_handler)
    app.add_exception_handler(Exception, exception_handler)
