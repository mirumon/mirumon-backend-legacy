from typing import List, Optional

from fastapi.security import OAuth2PasswordRequestForm

from app.domain.scopes import Scopes
from app.domain.user.user import User


class UserInLogin(OAuth2PasswordRequestForm):
    username: str
    password: str


class UserInCreate(User):
    username: str
    scopes: List[Scopes] = []


class UserInUpdate(User):
    username: Optional[str] = None
    password: Optional[str] = None
    scopes: List[str] = []