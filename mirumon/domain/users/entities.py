from dataclasses import dataclass
from typing import List, NewType
from uuid import UUID

from mirumon.domain.core.entity import Entity
from mirumon.domain.users.scopes import Scopes

UserID = NewType("UserID", UUID)
RawPassword = NewType("RawPassword", str)
HashedPassword = NewType("HashedPassword", str)
Username = NewType("Username", str)
AccessToken = NewType("AccessToken", str)


@dataclass
class User(Entity):
    id: UserID
    username: Username
    scopes: List[Scopes]
    salt: str
    hashed_password: HashedPassword
