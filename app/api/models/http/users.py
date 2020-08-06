from typing import List, Optional

from app.api.models.http.base import APIModel
from app.domain.user.scopes import Scopes
from app.domain.user.user import AccessToken, RawPassword, Username


class UserInCreate(APIModel):
    username: str
    password: RawPassword
    scopes: List[Scopes] = []


class UserInUpdate(APIModel):
    username: Optional[Username] = None
    password: Optional[RawPassword] = None
    scopes: List[Scopes] = []


class UserInLogin(APIModel):
    username: Username
    password: RawPassword


class UserToken(APIModel):
    access_token: AccessToken
    token_type: str
