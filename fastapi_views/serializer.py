from __future__ import annotations

from typing import Any, Literal, Mapping, Sequence, TypeVar

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
                from_attributes = (
                    True
                    if isinstance(obj, Mapping)
                    or (
                        isinstance(obj, Sequence)
                        and all(isinstance(el, Mapping) for el in obj)
                    )
                    else False
                )
            obj = self.validate_python(obj, from_attributes=from_attributes)
        return self.dump_json(obj, **options)
