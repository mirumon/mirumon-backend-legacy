from typing import Union

from mirumon.domain.core.enums import StrEnum


class DevicesScopes(StrEnum):
    read: str = "devices:read"
    write: str = "devices:write"


class UsersScopes(StrEnum):
    read: str = "users:read"
    write: str = "users:write"


Scopes = Union[DevicesScopes, UsersScopes]
