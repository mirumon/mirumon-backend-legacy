from typing import List, NewType, Optional
from uuid import UUID

from app.api.models.http.base import APIModel
from app.domain.user.scopes import Scopes

UserID = NewType("UserID", UUID)
RawPassword = NewType("RawPassword", str)
HashedPassword = NewType("HashedPassword", str)
Username = NewType("Username", str)
AccessToken = NewType("AccessToken", str)


class UserJWT(APIModel):
    username: str
    scopes: List[Scopes]


class User(APIModel):
    id: UserID
    username: Username
    scopes: List[Scopes]


class UserInDB(User):
    id: Optional[UserID]  # type: ignore
    salt: str
    hashed_password: HashedPassword  # type: ignore
