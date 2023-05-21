from functools import partial

from .functools import route

get = partial(route, methods=["GET"])
post = partial(route, methods=["POST"])
put = partial(route, methods=["PUT"])
patch = partial(route, methods=["PATCH"])
delete = partial(route, methods=["DELETE"])
