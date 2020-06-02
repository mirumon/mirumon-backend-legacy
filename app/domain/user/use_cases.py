from typing import List, NewType, Optional

from fastapi.security import OAuth2PasswordRequestForm

from app.components.core import APIModel
from app.domain.user.scopes import Scopes
from app.domain.user.user import User

RawPassword = NewType("RawPassword", str)


class UserInLogin(OAuth2PasswordRequestForm):
    username: str
    password: RawPassword


class UserToken(APIModel):
    access_token: str
    token_type: str


class UserInCreate(User):
    scopes: List[Scopes] = []


class UserInUpdate(User):
    username: Optional[str] = None
    password: Optional[RawPassword] = None
    scopes: List[str] = []
