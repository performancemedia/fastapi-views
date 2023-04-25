from abc import ABC

from .api import (
    AsyncCreateAPIView,
    AsyncDestroyAPIView,
    AsyncListAPIView,
    AsyncRetrieveAPIView,
    AsyncUpdateAPIView,
    CreateAPIView,
    DestroyAPIView,
    ListAPIView,
    RetrieveAPIView,
    UpdateAPIView,
)
from .generics import (
    AsyncGenericCreateView,
    AsyncGenericDestroyView,
    AsyncGenericListView,
    AsyncGenericRetrieveView,
    AsyncGenericUpdateView,
    GenericCreateView,
    GenericDestroyView,
    GenericListView,
    GenericRetrieveView,
    GenericUpdateView,
)


class ReadOnlyAPIViewSet(ListAPIView, RetrieveAPIView, ABC):
    ...


class AsyncReadOnlyAPIViewSet(AsyncListAPIView, AsyncRetrieveAPIView, ABC):
    ...


class ListCreateAPIViewSet(ListAPIView, CreateAPIView, ABC):
    ...


class AsyncListCreateAPIViewSet(AsyncListAPIView, AsyncCreateAPIView, ABC):
    ...


class RetrieveUpdateAPIViewSet(RetrieveAPIView, UpdateAPIView, ABC):
    ...


class AsyncRetrieveUpdateAPIViewSet(AsyncRetrieveAPIView, AsyncUpdateAPIView, ABC):
    ...


class RetrieveUpdateDestroyAPIViewSet(
    RetrieveAPIView, UpdateAPIView, DestroyAPIView, ABC
):
    ...


class AsyncRetrieveUpdateDestroyAPIViewSet(
    AsyncRetrieveAPIView, AsyncUpdateAPIView, AsyncDestroyAPIView, ABC
):
    ...


class ListRetrieveUpdateDestroyAPIViewSet(
    ListAPIView, RetrieveAPIView, UpdateAPIView, DestroyAPIView, ABC
):
    ...


class AsyncListRetrieveUpdateDestroyAPIViewSet(
    AsyncListAPIView, AsyncRetrieveAPIView, AsyncUpdateAPIView, AsyncDestroyAPIView, ABC
):
    ...


class ListCreateDestroyAPIViewSet(ListAPIView, CreateAPIView, DestroyAPIView, ABC):
    ...


class AsyncListCreateDestroyAPIViewSet(
    AsyncListAPIView, AsyncCreateAPIView, AsyncDestroyAPIView, ABC
):
    ...


class APIViewSet(
    ListAPIView, CreateAPIView, RetrieveAPIView, UpdateAPIView, DestroyAPIView, ABC
):
    ...


class AsyncAPIViewSet(
    AsyncListAPIView,
    AsyncCreateAPIView,
    AsyncRetrieveAPIView,
    AsyncUpdateAPIView,
    AsyncDestroyAPIView,
    ABC,
):
    ...


class GenericReadOnlyViewSet(GenericListView, GenericRetrieveView, ABC):
    ...


class AsyncGenericReadOnlyViewSet(AsyncGenericListView, AsyncGenericRetrieveView, ABC):
    ...


class GenericListCreateViewSet(GenericListView, GenericCreateView, ABC):
    ...


class AsyncGenericListCreateViewSet(AsyncGenericListView, AsyncGenericCreateView, ABC):
    ...


class GenericRetrieveUpdateViewSet(GenericRetrieveView, GenericUpdateView, ABC):
    ...


class AsyncGenericRetrieveUpdateViewSet(
    AsyncGenericRetrieveView, AsyncGenericUpdateView, ABC
):
    ...


class GenericRetrieveUpdateDestroyAPIViewSet(
    GenericRetrieveView, GenericUpdateView, GenericDestroyView, ABC
):
    ...


class AsyncGenericRetrieveUpdateDestroyAPIViewSet(
    AsyncGenericRetrieveView, AsyncGenericUpdateView, AsyncGenericDestroyView, ABC
):
    ...


class GenericListRetrieveUpdateDeleteViewSet(
    GenericListView, GenericRetrieveView, GenericUpdateView, GenericDestroyView, ABC
):
    ...


class AsyncGenericListRetrieveUpdateDeleteViewSet(
    AsyncGenericListView,
    AsyncGenericRetrieveView,
    AsyncGenericUpdateView,
    AsyncGenericDestroyView,
    ABC,
):
    ...


class GenericViewSet(
    GenericListView,
    GenericCreateView,
    GenericRetrieveView,
    GenericUpdateView,
    GenericDestroyView,
    ABC,
):
    ...


class AsyncGenericViewSet(
    AsyncGenericListView,
    AsyncGenericCreateView,
    AsyncGenericRetrieveView,
    AsyncGenericUpdateView,
    AsyncGenericDestroyView,
    ABC,
):
    ...
