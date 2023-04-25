from typing import Any, Iterable

from pydantic import BaseModel


class Serializer(BaseModel):
    @classmethod
    def parse(cls, obj: Any):
        if isinstance(obj, Serializer):
            return obj
        if isinstance(obj, dict):
            return cls.parse_obj(obj)
        if isinstance(obj, Iterable) and not isinstance(
            obj, (str, bytes, dict, BaseModel)
        ):
            return [cls.parse(o) for o in obj]
        else:
            return cls.from_orm(obj)

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        use_enum_values = True
