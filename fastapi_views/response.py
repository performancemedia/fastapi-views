from typing import Any

import orjson
from fastapi.responses import JSONResponse
from pydantic_core import to_jsonable_python


class JsonResponse(JSONResponse):
    def render(self, content: Any) -> bytes:
        if isinstance(content, bytes):
            return content
        return orjson.dumps(
            content,
            option=orjson.OPT_NON_STR_KEYS | orjson.OPT_SERIALIZE_NUMPY,
            default=to_jsonable_python,
        )
