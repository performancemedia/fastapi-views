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
    """ReadOnlyAPIViewSet"""


class AsyncReadOnlyAPIViewSet(AsyncListAPIView, AsyncRetrieveAPIView, ABC):
    """AsyncReadOnlyAPIViewSet"""


class ListCreateAPIViewSet(ListAPIView, CreateAPIView, ABC):
    """ListCreateAPIViewSet"""


class AsyncListCreateAPIViewSet(AsyncListAPIView, AsyncCreateAPIView, ABC):
    """AsyncListCreateAPIViewSet"""


class RetrieveUpdateAPIViewSet(RetrieveAPIView, UpdateAPIView, ABC):
    """RetrieveUpdateAPIViewSet"""


class AsyncRetrieveUpdateAPIViewSet(AsyncRetrieveAPIView, AsyncUpdateAPIView, ABC):
    """AsyncRetrieveUpdateAPIViewSet"""


class RetrieveUpdateDestroyAPIViewSet(
    RetrieveAPIView, UpdateAPIView, DestroyAPIView, ABC
):
    """RetrieveUpdateDestroyAPIViewSet"""


class AsyncRetrieveUpdateDestroyAPIViewSet(
    AsyncRetrieveAPIView, AsyncUpdateAPIView, AsyncDestroyAPIView, ABC
):
    """AsyncRetrieveUpdateDestroyAPIViewSet"""


class ListRetrieveUpdateDestroyAPIViewSet(
    ListAPIView, RetrieveAPIView, UpdateAPIView, DestroyAPIView, ABC
):
    """ListRetrieveUpdateDestroyAPIViewSet"""


class AsyncListRetrieveUpdateDestroyAPIViewSet(
    AsyncListAPIView, AsyncRetrieveAPIView, AsyncUpdateAPIView, AsyncDestroyAPIView, ABC
):
    """AsyncListRetrieveUpdateDestroyAPIViewSet"""


class ListCreateDestroyAPIViewSet(ListAPIView, CreateAPIView, DestroyAPIView, ABC):
    """ListCreateDestroyAPIViewSet"""


class AsyncListCreateDestroyAPIViewSet(
    AsyncListAPIView, AsyncCreateAPIView, AsyncDestroyAPIView, ABC
):
    """AsyncListCreateDestroyAPIViewSet"""


class APIViewSet(
    ListAPIView, CreateAPIView, RetrieveAPIView, UpdateAPIView, DestroyAPIView, ABC
):
    """APIViewSet"""


class AsyncAPIViewSet(
    AsyncListAPIView,
    AsyncCreateAPIView,
    AsyncRetrieveAPIView,
    AsyncUpdateAPIView,
    AsyncDestroyAPIView,
    ABC,
):
    """AsyncAPIViewSet"""


class GenericReadOnlyViewSet(GenericListView, GenericRetrieveView, ABC):
    """GenericReadOnlyViewSet"""


class AsyncGenericReadOnlyViewSet(AsyncGenericListView, AsyncGenericRetrieveView, ABC):
    """AsyncGenericReadOnlyViewSet"""


class GenericListCreateViewSet(GenericListView, GenericCreateView, ABC):
    """GenericListCreateViewSet"""


class AsyncGenericListCreateViewSet(AsyncGenericListView, AsyncGenericCreateView, ABC):
    """AsyncGenericListCreateViewSet"""


class GenericRetrieveUpdateViewSet(GenericRetrieveView, GenericUpdateView, ABC):
    """GenericRetrieveUpdateViewSet"""


class AsyncGenericRetrieveUpdateViewSet(
    AsyncGenericRetrieveView, AsyncGenericUpdateView, ABC
):
    """AsyncGenericRetrieveUpdateViewSet"""


class GenericRetrieveUpdateDestroyAPIViewSet(
    GenericRetrieveView, GenericUpdateView, GenericDestroyView, ABC
):
    """GenericRetrieveUpdateDestroyAPIViewSet"""


class AsyncGenericRetrieveUpdateDestroyAPIViewSet(
    AsyncGenericRetrieveView, AsyncGenericUpdateView, AsyncGenericDestroyView, ABC
):
    """AsyncGenericRetrieveUpdateDestroyAPIViewSet"""


class GenericListRetrieveUpdateDeleteViewSet(
    GenericListView, GenericRetrieveView, GenericUpdateView, GenericDestroyView, ABC
):
    """GenericListRetrieveUpdateDeleteViewSet"""


class AsyncGenericListRetrieveUpdateDeleteViewSet(
    AsyncGenericListView,
    AsyncGenericRetrieveView,
    AsyncGenericUpdateView,
    AsyncGenericDestroyView,
    ABC,
):
    """AsyncGenericListRetrieveUpdateDeleteViewSet"""


class GenericViewSet(
    GenericListView,
    GenericCreateView,
    GenericRetrieveView,
    GenericUpdateView,
    GenericDestroyView,
    ABC,
):
    """GenericViewSet"""


class AsyncGenericViewSet(
    AsyncGenericListView,
    AsyncGenericCreateView,
    AsyncGenericRetrieveView,
    AsyncGenericUpdateView,
    AsyncGenericDestroyView,
    ABC,
):
    """AsyncGenericViewSet"""
