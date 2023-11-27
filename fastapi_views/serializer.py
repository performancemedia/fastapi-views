from typing import Any, TypeVar

from pydantic import TypeAdapter

T = TypeVar("T")


class TypeSerializer(TypeAdapter[T]):
    def serialize(self, obj: Any, validate: bool = True, **options) -> bytes:
        if validate:
            obj = self.validate_python(obj)
        options.setdefault("by_alias", True)
        return self.dump_json(obj, **options)
