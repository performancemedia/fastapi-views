# mypy: ignore-errors
from typing import Any, Optional

from fastapi import Depends, Response
from pydantic import BaseModel
from starlette.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT

from ..types import AsyncRepository, Repository
from .api import (
    AsyncCreateAPIView,
    AsyncDestroyAPIView,
    AsyncListAPIView,
    AsyncPartialUpdateAPIView,
    AsyncRetrieveAPIView,
    AsyncUpdateAPIView,
    CreateAPIView,
    Endpoint,
    ListAPIView,
    PartialUpdateAPIView,
    RetrieveAPIView,
)
from .functools import catch_defined
from .mixins import GenericDetailViewMixin, GenericViewMixin


class GenericListView(ListAPIView, GenericViewMixin[Repository]):
    """Sync generic list view"""

    @classmethod
    def get_list_endpoint(cls) -> Endpoint:
        param_type = cls.get_params("list")

        def endpoint(
            self: GenericListView = Depends(cls),
            params: param_type = Depends(param_type),
        ):
            objects = self.list(**params.model_dump(exclude_none=True))
            return self.serialize_response("list", objects, status_code=HTTP_200_OK)

        cls._patch_metadata(endpoint, cls.list)
        return endpoint

    @catch_defined
    def list(self, **kwargs):
        return self.repository.list(**kwargs)


class AsyncGenericListView(AsyncListAPIView, GenericViewMixin[AsyncRepository]):
    """Async generic list view"""

    @classmethod
    def get_list_endpoint(cls):
        param_type = cls.get_params("list")

        async def endpoint(
            self: AsyncGenericListView = Depends(cls),
            params: param_type = Depends(param_type),
        ):
            objects = await self.list(**params.model_dump(exclude_none=True))
            return self.serialize_response("list", objects, status_code=HTTP_200_OK)

        cls._patch_metadata(endpoint, cls.list)
        return endpoint

    @catch_defined
    async def list(self, *args, **kwargs):
        return await self.repository.list(*args, **kwargs)


class GenericCreateView(CreateAPIView, GenericViewMixin[Repository]):
    """Sync generic create view"""

    create_schema: Optional[type[BaseModel]] = None

    @classmethod
    def get_create_endpoint(cls):
        param_type = cls.get_params("create")
        create_schema_type = cls.create_schema or cls.response_schema

        def endpoint(
            create_schema: create_schema_type,
            self: GenericCreateView = Depends(cls),
            params: param_type = Depends(param_type),
        ):
            obj = self.create(
                create_schema.model_dump(),
                **params.model_dump(exclude_none=True),
            )
            if self.return_on_create:
                return self.serialize_response(
                    "create", obj, status_code=HTTP_201_CREATED
                )
            return Response(status_code=HTTP_201_CREATED)

        cls._patch_metadata(endpoint, cls.create)
        return endpoint

    @catch_defined
    def create(self, entity, **kwargs):
        return self.repository.create(entity, **kwargs)


class AsyncGenericCreateView(AsyncCreateAPIView, GenericViewMixin[AsyncRepository]):
    """Async generic create view"""

    create_schema: Optional[type[BaseModel]] = None

    @classmethod
    def get_create_endpoint(cls):
        param_type = cls.get_params("create")
        create_schema_type = cls.create_schema or cls.response_schema

        async def endpoint(
            create_schema: create_schema_type,
            self: AsyncGenericCreateView = Depends(cls),
            params: param_type = Depends(param_type),
        ):
            obj = await self.create(
                create_schema.model_dump(),
                **params.model_dump(exclude_none=True),
            )
            if self.return_on_create:
                return self.serialize_response(
                    "create", obj, status_code=HTTP_201_CREATED
                )
            return Response(status_code=HTTP_201_CREATED)

        cls._patch_metadata(endpoint, cls.create)
        return endpoint

    @catch_defined
    async def create(self, entity, **kwargs):
        return await self.repository.create(entity, **kwargs)


class GenericRetrieveView(RetrieveAPIView, GenericDetailViewMixin[Repository]):
    """Sync generic retrieve view"""

    @classmethod
    def get_retrieve_endpoint(cls):
        param_type = cls.get_params("retrieve")
        pk_type = cls.pk

        def endpoint(
            self: GenericRetrieveView = Depends(cls),
            pk: pk_type = Depends(pk_type),
            params: param_type = Depends(param_type),
        ) -> Endpoint:
            kwargs = {
                **pk.model_dump(exclude_none=True),
                **params.model_dump(exclude_none=True),
            }
            obj = self.retrieve(**kwargs)
            if obj is None and self.raise_on_none:
                self.raise_not_found_error()
            return self.serialize_response("retrieve", obj)

        cls._patch_metadata(endpoint, cls.retrieve)
        return endpoint

    @catch_defined
    def retrieve(self, **kwargs) -> Any:
        return self.repository.retrieve(**kwargs)


class AsyncGenericRetrieveView(
    AsyncRetrieveAPIView, GenericDetailViewMixin[AsyncRepository]
):
    """Async generic retrieve view"""

    @classmethod
    def get_retrieve_endpoint(cls) -> Endpoint:
        param_type = cls.get_params("retrieve")
        pk_type = cls.pk

        async def endpoint(
            self: AsyncGenericRetrieveView = Depends(cls),
            pk: pk_type = Depends(pk_type),
            params: param_type = Depends(param_type),
        ):
            kwargs = {
                **pk.model_dump(exclude_none=True),
                **params.model_dump(exclude_none=True),
            }

            obj = await self.retrieve(**kwargs)
            if obj is None:
                self.raise_not_found_error()
            return self.serialize_response("retrieve", obj)

        cls._patch_metadata(endpoint, cls.retrieve)

        return endpoint

    @catch_defined
    async def retrieve(self, *args, **kwargs):
        return await self.repository.retrieve(*args, **kwargs)


class GenericUpdateView(AsyncUpdateAPIView, GenericDetailViewMixin[Repository]):
    """Sync generic update view"""

    update_schema: Optional[type[BaseModel]] = None

    @classmethod
    def get_update_endpoint(cls) -> Endpoint:
        param_type = cls.get_params("update")
        pk_type = cls.pk
        update_schema_type = cls.update_schema or cls.response_schema

        def endpoint(
            update_schema: update_schema_type,
            self: GenericUpdateView = Depends(cls),
            pk: pk_type = Depends(pk_type),
            params: param_type = Depends(param_type),
        ):
            kwargs = {
                **pk.model_dump(exclude_none=True),
                **params.model_dump(exclude_none=True),
            }

            obj = self.update(update_schema.model_dump(), **kwargs)
            if self.return_on_update:
                return self.serialize_response("update", obj)
            return Response(status_code=HTTP_200_OK)

        cls._patch_metadata(endpoint, cls.update)
        return endpoint

    @catch_defined
    def update(self, *args, **kwargs) -> Any:
        return self.repository.update(*args, **kwargs)


class AsyncGenericUpdateView(
    AsyncUpdateAPIView, GenericDetailViewMixin[AsyncRepository]
):
    """Async generic update view"""

    update_schema: Optional[type[BaseModel]] = None

    @classmethod
    def get_update_endpoint(cls) -> Endpoint:
        param_type = cls.get_params("update")
        pk_type = cls.pk
        update_schema_type = cls.update_schema or cls.response_schema

        async def endpoint(
            update_schema: update_schema_type,
            self: AsyncGenericUpdateView = Depends(cls),
            pk: pk_type = Depends(pk_type),
            params: param_type = Depends(param_type),
        ):
            kwargs = {
                **pk.model_dump(exclude_none=True),
                **params.model_dump(exclude_none=True),
            }
            obj = await self.update(update_schema.model_dump(), **kwargs)
            if self.return_on_update:
                return self.serialize_response("update", obj)
            return Response(status_code=HTTP_200_OK)

        cls._patch_metadata(endpoint, cls.update)
        return endpoint

    @catch_defined
    async def update(self, entity, **kwargs) -> Any:
        return await self.repository.update(entity, **kwargs)


class GenericPartialUpdateView(
    PartialUpdateAPIView, GenericDetailViewMixin[Repository]
):
    """Sync generic partial update view"""

    partial_update_schema: Optional[type[BaseModel]] = None

    @classmethod
    def get_partial_update_endpoint(cls) -> Endpoint:
        param_type = cls.get_params("partial_update")
        pk_type = cls.pk
        partial_update_schema_type = cls.partial_update_schema or cls.response_schema

        def endpoint(
            partial_update_schema: partial_update_schema_type,
            self=Depends(cls),
            pk=Depends(pk_type),
            params=Depends(param_type),
        ):
            kwargs = {
                **pk.model_dump(exclude_none=True),
                **params.model_dump(exclude_none=True),
            }
            obj = self.partial_update(partial_update_schema.model_dump(), **kwargs)
            if self.return_on_update:
                return self.serialize_response("partial_update", obj)
            return Response(status_code=HTTP_200_OK)

        cls._patch_metadata(endpoint, cls.partial_update)
        return endpoint

    @catch_defined
    def partial_update(self, *args, **kwargs) -> Any:
        return self.repository.update(*args, **kwargs)


class AsyncGenericPartialUpdateView(
    AsyncPartialUpdateAPIView, GenericDetailViewMixin[AsyncRepository]
):
    """Async generic partial update view"""

    partial_update_schema: Optional[type[BaseModel]] = None

    @classmethod
    def get_partial_update_endpoint(cls):
        param_type = cls.get_params("partial_update")
        pk_type = cls.pk
        partial_update_schema_type = cls.partial_update_schema or cls.response_schema

        async def endpoint(
            partial_update_schema: partial_update_schema_type,
            self=Depends(cls),
            pk=Depends(pk_type),
            params=Depends(param_type),
        ):
            kwargs = {
                **pk.model_dump(exclude_none=True),
                **params.model_dump(exclude_none=True),
            }
            obj = await self.partial_update(
                partial_update_schema=partial_update_schema, **kwargs
            )
            if self.return_on_update:
                return self.serialize_response("partial_update", obj)
            return Response(status_code=HTTP_200_OK)

        cls._patch_metadata(endpoint, cls.partial_update)
        return endpoint

    @catch_defined
    async def partial_update(self, *args, **kwargs) -> Any:
        return await self.repository.update(*args, **kwargs)


class GenericDestroyView(AsyncDestroyAPIView, GenericDetailViewMixin[Repository]):
    """Sync generic destroy view"""

    @classmethod
    def get_destroy_endpoint(cls) -> Endpoint:
        param_type = cls.get_params("destroy")
        pk_type = cls.pk

        def endpoint(
            self=Depends(cls), pk=Depends(pk_type), params=Depends(param_type)
        ):
            kwargs = {
                **pk.model_dump(exclude_none=True),
                **params.model_dump(exclude_none=True),
            }
            self.destroy(**kwargs)
            return Response(status_code=HTTP_204_NO_CONTENT)

        cls._patch_metadata(endpoint, cls.destroy)
        return endpoint

    @catch_defined
    def destroy(self, **kwargs) -> None:
        self.repository.delete(**kwargs)


class AsyncGenericDestroyView(
    AsyncDestroyAPIView, GenericDetailViewMixin[AsyncRepository]
):
    """Async generic destroy view"""

    @classmethod
    def get_destroy_endpoint(cls) -> Endpoint:
        param_type = cls.get_params("destroy")
        pk_type = cls.pk

        async def endpoint(
            self=Depends(cls), pk=Depends(pk_type), params=Depends(param_type)
        ):
            kwargs = {
                **pk.model_dump(exclude_none=True),
                **params.model_dump(exclude_none=True),
            }
            await self.destroy(**kwargs)
            return Response(status_code=HTTP_204_NO_CONTENT)

        cls._patch_metadata(endpoint, cls.destroy)
        return endpoint

    @catch_defined
    async def destroy(self, *args, **kwargs) -> None:
        await self.repository.delete(*args, **kwargs)
