from datetime import datetime
from typing import List, NewType, Optional
from uuid import UUID

from app.domain.user.scopes import Scopes, UserScopes
from app.settings.components.core import APIModel

UserID = NewType("UserID", UUID)
RawPassword = NewType("RawPassword", str)
HashedPassword = NewType("HashedPassword", str)
Username = NewType("Username", str)
AccessToken = NewType("AccessToken", str)


class User(APIModel):
    id: UserID
    username: Username
    scopes: List[Scopes]


class UserInCreate(APIModel):
    username: str
    password: RawPassword
    scopes: List[Scopes] = []


class UserInUpdate(APIModel):
    username: Optional[Username] = None
    password: Optional[RawPassword] = None
    scopes: List[str] = []


class UserInLogin(APIModel):
    username: Username
    password: RawPassword


class UserToken(APIModel):
    access_token: AccessToken
    token_type: str


class MetaJWT(APIModel):
    exp: datetime
    sub: str


class UserJWT(APIModel):
    username: str
    scopes: List[Scopes] = [UserScopes.read]


class UserInDB(User):
    id: Optional[UserID]
    salt: str = ""
    hashed_password: HashedPassword = ""
