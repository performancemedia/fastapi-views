from fastapi import Request
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

from ..response import JsonResponse
from .exceptions import APIError
from .models import ErrorDetails, InternalServerAPIError
from .utils import find_model_for_exc


def api_error_handler(request: Request, exc: APIError):
    return JsonResponse(
        status_code=exc.status,
        content=ErrorDetails(
            detail=exc.detail,
            title=exc.title,
            status=exc.status,
            instance=exc.instance or request.url.path,
        ).dict(),
    )


def exception_handler(request, exc: Exception):
    model_cls = find_model_for_exc(type(exc).__name__)
    detail = getattr(exc, "detail", str(exc))
    if model_cls:
        model = model_cls(detail=detail, instance=request.url.path)
        return JsonResponse(status_code=model.status, content=model.dict())
    return JsonResponse(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        content=InternalServerAPIError(
            detail=detail,
            instance=request.url.path,
        ).dict(),
    )


def add_error_handlers(app):
    app.add_exception_handler(APIError, api_error_handler)
    app.add_exception_handler(Exception, exception_handler)
