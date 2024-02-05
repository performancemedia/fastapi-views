from inspect import isabstract

from fastapi import APIRouter

from .views.api import View


def register_view(router: APIRouter, view: type[View], prefix: str = ""):
    if isabstract(view):
        raise TypeError(f"Cannot register abstract view {view}")
    for route_params in view.get_api_actions(prefix):
        router.add_api_route(**route_params)


class ViewRouter(APIRouter):
    register_view = register_view
