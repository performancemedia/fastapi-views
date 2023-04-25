from typing import Any, Generic, Type, TypeVar, Union
from uuid import UUID

from fastapi import Depends, Response
from pydantic import BaseModel
from starlette.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT

from ..serializer import Serializer
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
    RetrieveAPIView,
)
from .functools import catch_defined
from .mixins import ErrorHandlerMixin

P = TypeVar("P", bound=Type[BaseModel])
R = TypeVar("R", bound=Union[AsyncRepository, Repository])


class PK(BaseModel):
    id: UUID


class GenericViewMixin(ErrorHandlerMixin, Generic[P, R]):
    params: P = BaseModel
    repository: R

    @classmethod
    def get_params(cls, action: str) -> P:
        return cls.params


class GenericListView(ListAPIView, GenericViewMixin[P, Repository]):
    @classmethod
    def get_list_endpoint(cls) -> Endpoint:
        param_type = cls.get_params("list")

        def endpoint(
            self: GenericListView = Depends(cls),
            params=Depends(param_type),
        ):
            objects = self.list(**params.dict(exclude_none=True))  # type: ignore[attr-defined]
            return self.serialize_response("list", objects, status_code=HTTP_200_OK)

        cls._patch_metadata(endpoint, cls.list)
        return endpoint

    @catch_defined
    def list(self, *args, **kwargs):
        return self.repository.list(*args, **kwargs)


class AsyncGenericListView(AsyncListAPIView, GenericViewMixin[P, AsyncRepository]):
    @classmethod
    def get_list_endpoint(cls):
        param_type = cls.get_params("list")

        async def endpoint(
            self: AsyncGenericListView = Depends(cls),
            params: param_type = Depends(param_type),
        ):
            objects = await self.list(**params.dict(exclude_none=True))  # type: ignore[attr-defined]
            return self.serialize_response("list", objects, status_code=HTTP_200_OK)

        cls._patch_metadata(endpoint, cls.list)
        return endpoint

    @catch_defined
    async def list(self, *args, **kwargs):
        return await self.repository.list(*args, **kwargs)


class GenericCreateView(CreateAPIView, GenericViewMixin[P, Repository]):
    create_serializer: Type[Serializer]

    @classmethod
    def get_create_endpoint(cls):
        create_serializer_type = cls.create_serializer
        param_type = cls.get_params("create")

        def endpoint(
            create_serializer: create_serializer_type,
            self: GenericCreateView = Depends(cls),
            params: param_type = Depends(param_type),
        ):

            obj = self.create(
                create_serializer=create_serializer,
                **params.dict(exclude_none=True),  # type: ignore[attr-defined]
            )
            if self.return_on_create:
                return self.serialize_response(
                    "create", obj, status_code=HTTP_201_CREATED
                )
            return Response(status_code=HTTP_201_CREATED)

        cls._patch_metadata(endpoint, cls.create)
        return endpoint

    @catch_defined
    def create(self, *args, **kwargs):
        return self.repository.create(*args, **kwargs)


class AsyncGenericCreateView(AsyncCreateAPIView, GenericViewMixin[P, AsyncRepository]):
    create_serializer: Type[Serializer]

    @classmethod
    def get_create_endpoint(cls):
        create_serializer_type = cls.create_serializer
        param_type = cls.get_params("create")

        async def endpoint(
            create_serializer: create_serializer_type,
            self: AsyncGenericCreateView = Depends(cls),
            params: param_type = Depends(param_type),
        ):

            obj = await self.create(
                create_serializer=create_serializer,
                **params.dict(exclude_none=True),  # type: ignore[attr-defined]
            )
            if self.return_on_create:
                return self.serialize_response(
                    "create", obj, status_code=HTTP_201_CREATED
                )
            return Response(status_code=HTTP_201_CREATED)

        cls._patch_metadata(endpoint, cls.create)
        return endpoint

    @catch_defined
    async def create(self, *args, **kwargs):
        return await self.repository.create(*args, **kwargs)


class GenericRetrieveView(RetrieveAPIView, GenericViewMixin[P, Repository]):
    pk: Type[BaseModel] = PK

    @classmethod
    def get_retrieve_endpoint(cls):
        def endpoint(
            self: GenericRetrieveView = Depends(cls),
            pk=Depends(cls.pk),
            params: BaseModel = Depends(cls.get_params("retrieve")),
        ) -> Endpoint:
            kwargs = {**pk.dict(exclude_none=True), **params.dict(exclude_none=True)}  # type: ignore[attr-defined]

            obj = self.retrieve(**kwargs)
            if obj is None:
                self.raise_not_found_error()
            return self.serialize_response("retrieve", obj)

        cls._patch_metadata(endpoint, cls.retrieve)
        return endpoint

    @catch_defined
    def retrieve(self, *args, **kwargs) -> Any:
        return self.repository.retrieve(*args, **kwargs)


class AsyncGenericRetrieveView(
    AsyncRetrieveAPIView, GenericViewMixin[P, AsyncRepository]
):
    pk: Type[BaseModel] = PK

    @classmethod
    def get_retrieve_endpoint(cls) -> Endpoint:
        async def endpoint(
            self: AsyncGenericRetrieveView = Depends(cls),
            pk: BaseModel = Depends(cls.pk),
            params: BaseModel = Depends(cls.get_params("retrieve")),
        ):
            kwargs = {**pk.dict(exclude_none=True), **params.dict(exclude_none=True)}  # type: ignore[attr-defined]

            obj = await self.retrieve(**kwargs)
            if obj is None:
                self.raise_not_found_error()
            return self.serialize_response("retrieve", obj)

        cls._patch_metadata(endpoint, cls.retrieve)
        return endpoint

    @catch_defined
    async def retrieve(self, *args, **kwargs):
        return await self.repository.retrieve(*args, **kwargs)


class GenericUpdateView(AsyncUpdateAPIView, GenericViewMixin[P, Repository]):
    update_serializer: Type[Serializer]
    pk: Type[BaseModel] = PK

    @classmethod
    def get_update_endpoint(cls) -> Endpoint:
        def endpoint(
            update_serializer=Depends(cls.update_serializer),
            self: GenericUpdateView = Depends(cls),
            pk: BaseModel = Depends(cls.pk),
            params: P = Depends(cls.get_params("update")),
        ):
            kwargs = {**pk.dict(exclude_none=True), **params.dict(exclude_none=True)}  # type: ignore[attr-defined]

            obj = self.update(update_serializer=update_serializer, **kwargs)
            if self.return_on_update:
                return self.serialize_response("update", obj)
            return Response(status_code=HTTP_200_OK)

        cls._patch_metadata(endpoint, cls.update)
        return endpoint

    @catch_defined
    def update(self, *args, **kwargs) -> Any:
        return self.repository.update(*args, **kwargs)


class AsyncGenericUpdateView(AsyncUpdateAPIView, GenericViewMixin[P, AsyncRepository]):
    update_serializer: Type[Serializer]
    pk: Type[BaseModel] = PK

    @classmethod
    def get_update_endpoint(cls) -> Endpoint:
        async def endpoint(
            self: GenericUpdateView = Depends(cls),
            update_serializer: Serializer = Depends(cls.update_serializer),
            pk: PK = Depends(cls.pk),
            params: P = Depends(cls.get_params("update")),
        ):
            kwargs = {**pk.dict(exclude_none=True), **params.dict(exclude_none=True)}  # type: ignore[attr-defined]

            obj = await self.update(update_serializer=update_serializer, **kwargs)
            if self.return_on_update:
                return self.serialize_response("update", obj)
            return Response(status_code=HTTP_200_OK)

        cls._patch_metadata(endpoint, cls.update)
        return endpoint

    @catch_defined
    async def update(self, *args, **kwargs) -> Any:
        return await self.repository.update(*args, **kwargs)


class GenericPartialUpdateView(
    AsyncPartialUpdateAPIView, GenericViewMixin[P, Repository]
):
    partial_update_serializer: Type[BaseModel]
    pk: Type[BaseModel] = PK

    @classmethod
    def get_partial_update_endpoint(cls) -> Endpoint:
        def endpoint(
            self: AsyncGenericPartialUpdateView = Depends(cls),
            partial_update_serializer: BaseModel = Depends(
                cls.partial_update_serializer
            ),
            pk: BaseModel = Depends(cls.pk),
            params: P = Depends(cls.get_params("partial_update")),
        ):
            kwargs = {**pk.dict(exclude_none=True), **params.dict(exclude_none=True)}  # type: ignore[attr-defined]
            obj = self.partial_update(
                partial_update_serializer=partial_update_serializer, **kwargs
            )
            if self.return_on_update:
                return self.serialize_response("partial_update", obj)
            return Response(status_code=HTTP_200_OK)

        cls._patch_metadata(endpoint, cls.partial_update)
        return endpoint

    @catch_defined
    def partial_update(self, *args, **kwargs) -> Any:
        return self.repository.partial_update(*args, **kwargs)


class AsyncGenericPartialUpdateView(
    AsyncPartialUpdateAPIView, GenericViewMixin[P, AsyncRepository]
):
    partial_update_serializer: Type[BaseModel]
    pk: Type[BaseModel] = PK

    @classmethod
    def get_partial_update_endpoint(cls):
        async def endpoint(
            self: AsyncGenericPartialUpdateView = Depends(cls),
            partial_update_serializer: BaseModel = Depends(
                cls.partial_update_serializer
            ),
            pk: BaseModel = Depends(cls.pk),
            params: P = Depends(cls.get_params("partial_update")),
        ):
            kwargs = {**pk.dict(exclude_none=True), **params.dict(exclude_none=True)}  # type: ignore[attr-defined]
            obj = await self.partial_update(
                partial_update_serializer=partial_update_serializer, **kwargs
            )
            if self.return_on_update:
                return self.serialize_response("partial_update", obj)
            return Response(status_code=HTTP_200_OK)

        cls._patch_metadata(endpoint, cls.partial_update)
        return endpoint

    @catch_defined
    async def partial_update(self, *args, **kwargs) -> Any:
        return await self.repository.partial_update(*args, **kwargs)


class GenericDestroyView(AsyncDestroyAPIView, GenericViewMixin[P, Repository]):
    pk: Type[BaseModel] = PK

    @classmethod
    def get_destroy_endpoint(cls) -> Endpoint:
        def endpoint(
            self: GenericDestroyView = Depends(cls),
            pk: BaseModel = Depends(cls.pk),
            params: P = Depends(cls.get_params("destroy")),
        ):
            kwargs = {**pk.dict(exclude_none=True), **params.dict(exclude_none=True)}  # type: ignore[attr-defined]
            self.destroy(**kwargs)
            return Response(status_code=HTTP_204_NO_CONTENT)

        cls._patch_metadata(endpoint, cls.destroy)
        return endpoint

    @catch_defined
    def destroy(self, *args, **kwargs) -> None:
        self.repository.delete(*args, **kwargs)


class AsyncGenericDestroyView(
    AsyncDestroyAPIView, GenericViewMixin[P, AsyncRepository]
):
    pk: Type[BaseModel] = PK

    @classmethod
    def get_destroy_endpoint(cls) -> Endpoint:
        async def endpoint(
            self: AsyncGenericDestroyView = Depends(cls),
            pk: BaseModel = Depends(cls.pk),
            params: BaseModel = Depends(cls.get_params("destroy")),
        ):
            kwargs = {**pk.dict(exclude_none=True), **params.dict(exclude_none=True)}  # type: ignore[attr-defined]
            await self.destroy(**kwargs)
            return Response(status_code=HTTP_204_NO_CONTENT)

        cls._patch_metadata(endpoint, cls.destroy)
        return endpoint

    @catch_defined
    async def destroy(self, *args, **kwargs) -> None:
        await self.repository.delete(*args, **kwargs)
