from enum import Enum


class StrEnum(str, Enum):  # noqa: WPS600
    """Base class for string enums."""

    def __str__(self) -> str:  # pragma: no cover
        return self.value
