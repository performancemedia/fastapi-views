from typing import cast

from fastapi import APIRouter
from pydantic import BaseModel

from .views.api import View
from .views.viewsets import AsyncGenericViewSet, GenericViewSet


def register_view(router: APIRouter, view: type[View], prefix: str = ""):
    for route_params in view.get_api_actions(prefix):
        router.add_api_route(**route_params)


class ViewRouter(APIRouter):
    register_view = register_view


class CrudRouter(ViewRouter):
    def __init__(
        self,
        name: str,
        repository,
        pk: type[BaseModel],
        serializer,
        create_serializer=None,
        update_serializer=None,
        is_async: bool = True,
        **extra
    ):
        super().__init__(**extra)
        bases = (AsyncGenericViewSet,) if is_async else (GenericViewSet,)
        crud_viewset = cast(
            type[AsyncGenericViewSet],
            type(
                "GenericCrudViewset",
                bases,
                {
                    "pk": pk,
                    "repository": repository,
                    "serializer": serializer,
                    "api_component_name": name,
                    "create_serializer": create_serializer,
                    "update_serializer": update_serializer,
                },
            ),
        )
        register_view(self, crud_viewset)
