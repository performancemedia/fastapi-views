from typing import Optional

from pydantic import BaseModel, Field
from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
    HTTP_500_INTERNAL_SERVER_ERROR,
    HTTP_503_SERVICE_UNAVAILABLE,
)


class ErrorDetails(BaseModel):
    """
    Base Model for https://www.rfc-editor.org/rfc/rfc7807
    """

    type: str = Field(
        "about:blank",
        description="Error type",
    )
    title: Optional[str] = Field("Bad Request", description="Error title")
    status: int = Field(HTTP_400_BAD_REQUEST, description="Error status")
    detail: str = Field(
        ...,
        description="Error detail",
    )
    instance: Optional[str] = Field(None, description="Requested instance")

    @classmethod
    def from_exception(
        cls, exc: Exception, status_code: int = HTTP_400_BAD_REQUEST, **kwargs
    ):
        return cls(
            detail=str(exc), type=type(exc).__name__, status=status_code, **kwargs
        )

    @classmethod
    def get_status(cls) -> int:
        return cls.__fields__["status"].default

    class Config:
        allow_population_by_field_name = True
        use_enum_values = True


class NotFoundAPIError(ErrorDetails):
    title: str = Field("Not Found", const=True)
    status: int = Field(HTTP_404_NOT_FOUND, const=True)


class ConflictAPIError(ErrorDetails):
    title: str = Field("Conflict", const=True)
    status: int = Field(HTTP_409_CONFLICT, const=True)


class ServiceUnavailableAPIError(ErrorDetails):
    title: str = Field("Service Unavailable", const=True)
    status: int = Field(HTTP_503_SERVICE_UNAVAILABLE, const=True)


class InternalServerAPIError(ErrorDetails):
    title: str = Field("Internal Server Error", const=True)
    status: int = Field(HTTP_500_INTERNAL_SERVER_ERROR, const=True)
