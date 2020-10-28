from dataclasses import dataclass
from typing import List, NewType
from uuid import UUID

from app.domain.core.model import DomainModel
from app.domain.users.scopes import Scopes

UserID = NewType("UserID", UUID)
RawPassword = NewType("RawPassword", str)
HashedPassword = NewType("HashedPassword", str)
Username = NewType("Username", str)
AccessToken = NewType("AccessToken", str)


@dataclass
class User(DomainModel):
    id: UserID
    username: Username
    scopes: List[Scopes]
    salt: str
    hashed_password: HashedPassword
