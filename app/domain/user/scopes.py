from enum import Enum
from typing import Union


class UserScopes(str, Enum):  # noqa: WPS600
    execute: str = "users:execute"
    read: str = "users:read"

    def __str__(self) -> str:  # pragma: no cover
        return self.value


class AdministrationScopes(str, Enum):  # noqa: WPS600
    view: str = "admin:view"
    edit: str = "admin:edit"

    def __str__(self) -> str:  # pragma: no cover
        return self.value


Scopes = Union[UserScopes, AdministrationScopes]
