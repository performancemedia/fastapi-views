from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, Literal, TypeVar

from pydantic import TypeAdapter

T = TypeVar("T")


class TypeSerializer(TypeAdapter[T]):
    def serialize(
        self,
        obj: Any,
        *,
        validate: bool = True,
        from_attributes: bool | Literal["auto"] = True,
        **options: Any,
    ) -> bytes:
        if validate:
            if from_attributes == "auto":
                from_attributes = not isinstance(obj, Mapping) or (
                    isinstance(obj, Sequence)
                    and all(isinstance(el, Mapping) for el in obj)
                )
            obj = self.validate_python(obj, from_attributes=from_attributes)
        return self.dump_json(obj, **options)
