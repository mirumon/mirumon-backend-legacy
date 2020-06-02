from enum import Enum
from typing import Union


class UserScopes(str, Enum):  # noqa: WPS600
    execute: str = "users:execute"
    read: str = "users:read"


class AdministrationScopes(str, Enum):  # noqa: WPS600
    view: str = "admin:view"
    edit: str = "admin:edit"


Scopes = Union[UserScopes, AdministrationScopes, str]
