from typing import List, NewType, Optional
from uuid import UUID

from app.components.core import APIModel
from app.domain.user.scopes import Scopes

UserUID = NewType("UserUID", UUID)
RawPassword = NewType("RawPassword", str)


class User(APIModel):
    id: UserUID
    username: str
    scopes: List[Scopes]


class UserInCreate(APIModel):
    username: str
    password: RawPassword
    scopes: List[Scopes] = []


class UserInDB(User):
    salt: str = ""
    hashed_password: str = ""


class UserInLogin(APIModel):
    username: str
    password: RawPassword


class UserToken(APIModel):
    access_token: str
    token_type: str


class UserInUpdate(User):
    username: Optional[str] = None
    password: Optional[RawPassword] = None
    scopes: List[str] = []