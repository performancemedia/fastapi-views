from typing import Any

import orjson
from fastapi.responses import JSONResponse
from pydantic.json import pydantic_encoder


class JsonResponse(JSONResponse):
    media_type = "application/json"

    def render(self, content: Any) -> bytes:
        return orjson.dumps(
            content,
            option=orjson.OPT_NON_STR_KEYS | orjson.OPT_SERIALIZE_NUMPY,
            default=pydantic_encoder,
        )
