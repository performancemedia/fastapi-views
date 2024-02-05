from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class BaseSchema(BaseModel):
    model_config = ConfigDict(
        use_enum_values=True, populate_by_name=True, from_attributes=True
    )


class CamelCaseSchema(BaseSchema):
    model_config = ConfigDict(alias_generator=to_camel)


class IdSchema(BaseSchema):
    id: UUID = Field(..., description="Entity ID")


class CreatedUpdatedSchema(BaseSchema):
    created_at: datetime = Field(..., description="Timestamp when entity was created")
    updated_at: datetime = Field(
        ..., description="Timestamp when entity was last updated"
    )


class IdCreatedUpdatedSchema(IdSchema, CreatedUpdatedSchema):
    pass
