from fastapi import APIRouter

from .views.api import View


def register_view(router: APIRouter, view: View, prefix: str = ""):
    for route_params in view.get_api_actions(prefix):
        router.add_api_route(**route_params)


class ViewRouter(APIRouter):
    register_view = register_view
