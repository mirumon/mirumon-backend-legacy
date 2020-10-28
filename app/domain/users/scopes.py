from typing import Union

from app.domain.core.enum import StrEnum


class DevicesScopes(StrEnum):
    read: str = "devices:read"
    write: str = "devices:write"

    def __str__(self) -> str:  # pragma: no cover
        return self.value


class UsersScopes(StrEnum):
    read: str = "users:read"
    write: str = "users:write"

    def __str__(self) -> str:  # pragma: no cover
        return self.value


Scopes = Union[DevicesScopes, UsersScopes]
