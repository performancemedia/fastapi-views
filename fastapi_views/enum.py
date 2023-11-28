from __future__ import annotations

from enum import Enum, auto

from pydantic.alias_generators import to_camel


class StrEnum(str, Enum):
    """
    StrEnum subclasses that create variants using `auto()` will have values equal to their names
    Enums inheriting from this class that set values using `enum.auto()` will have variant values equal to their names
    """

    def __repr__(self) -> str:
        return f"{type(self).__name__}.{self.value}"


class AutoStrEnum(StrEnum):
    @staticmethod
    def auto():
        """
        Exposes `enum.auto()` to avoid requiring a second import to use `AutoEnum`
        """
        return auto()

    def _generate_next_value_(name, start, count, last_values) -> str:  # type: ignore
        """
        Uses the name as the automatic value, rather than an integer

        See https://docs.python.org/3/library/enum.html#using-automatic-values for reference
        """
        return name


class CamelStrEnum(str, Enum):
    """
    CamelStrEnum subclasses that create variants using `auto()` will have values equal to their camelCase names
    """

    # noinspection PyMethodParameters
    def _generate_next_value_(name, start, count, last_values) -> str:  # type: ignore
        return to_camel(name)


class CamelCaseAutoEnum(AutoStrEnum):
    def _generate_next_value_(name, start, count, last_values) -> str:  # type: ignore
        return to_camel(name)
