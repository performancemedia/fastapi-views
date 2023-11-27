from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic.fields import FieldInfo
from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
    HTTP_429_TOO_MANY_REQUESTS,
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

    @field_validator("detail", mode="before")
    @classmethod
    def validate_detail(cls, v):
        return v or "Internal Server Error"

    @classmethod
    def get_status(cls) -> int:
        return cls.model_fields["status"].get_default()

    model_config = ConfigDict(use_enum_values=True, populate_by_name=True)

    def __init_subclass__(cls, **kwargs):
        if title := kwargs.get("title"):
            FieldInfo().merge_field_infos()
            cls.model_fields["title"] = FieldInfo(
                default=title, annotation=Literal[title]
            )
        if status := kwargs.get("status"):
            cls.model_fields["status"] = FieldInfo(
                default=status, annotation=Literal[status]
            )


class NotFoundErrorDetails(ErrorDetails, title="Not Found", status=HTTP_404_NOT_FOUND):
    pass


class TooManyRequestsErrorDetails(
    ErrorDetails, title="Too many requests", status=HTTP_429_TOO_MANY_REQUESTS
):
    pass


class ConflictErrorDetails(ErrorDetails, title="Conflict", status=HTTP_409_CONFLICT):
    pass


class ServiceUnavailableErrorDetails(
    ErrorDetails, title="Service Unavailable", status=HTTP_503_SERVICE_UNAVAILABLE
):
    pass


class InternalServerErrorDetails(
    ErrorDetails, title="Internal Server Error", status=HTTP_500_INTERNAL_SERVER_ERROR
):
    pass
