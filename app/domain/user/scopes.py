from enum import Enum
from typing import Union


class DevicesScopes(str, Enum):  # noqa: WPS600
    read: str = "devices:read"
    write: str = "devices:write"

    def __str__(self) -> str:  # pragma: no cover
        return self.value


class UsersScopes(str, Enum):  # noqa: WPS600
    read: str = "users:read"
    write: str = "users:write"

    def __str__(self) -> str:  # pragma: no cover
        return self.value


Scopes = Union[DevicesScopes, UsersScopes]
