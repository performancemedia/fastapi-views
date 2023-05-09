import copy
from collections.abc import Iterable
from functools import partial
from typing import Any, Optional, cast

from pydantic import BaseModel

from fastapi_views.utils import snake2camel


def _make_optional(field):
    new_field = copy.copy(field)
    new_field.required = False
    new_field.allow_none = True
    new_field.default = None
    return new_field


class APIModel(BaseModel):
    @classmethod
    def subclass(
        cls,
        name: Optional[str] = None,
        exclude: Optional[set[str]] = None,
        partial: bool = False,
    ) -> type[BaseModel]:
        _exclude = exclude or set()
        new_cls = type(
            name or f"Partial{cls.__name__}",
            (cls,),
            {
                "__fields__": {
                    k: _make_optional(v) if partial else v
                    for k, v in cls.__fields__.items()
                    if k not in _exclude
                }
            },
        )
        return cast(type[BaseModel], new_cls)

    class Config:
        use_enum_values = True
        allow_population_by_field_name = True
        orm_mode = True


class CamelCaseAPIModel(APIModel):
    class Config:
        alias_generator = partial(snake2camel, start_lower=True)


class Serializer(APIModel):
    @classmethod
    def parse(cls, obj: Any):
        if isinstance(obj, cls):
            return obj
        if isinstance(obj, (dict, BaseModel)):
            return cls.parse_obj(obj)
        if isinstance(obj, Iterable) and not isinstance(
            obj, (str, bytes, dict, BaseModel)
        ):
            return [cls.parse(o) for o in obj]
        else:
            return cls.from_orm(obj)


class CamelCaseSerializer(Serializer):
    class Config:
        alias_generator = partial(snake2camel, start_lower=True)
