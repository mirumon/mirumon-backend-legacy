from datetime import datetime
from typing import List

from pydantic import BaseModel

from app.domain.user.scopes import Scopes


class JWTMeta(BaseModel):
    exp: datetime
    sub: str


class User(BaseModel):
    username: str
    scopes: List[Scopes]


class UserToken(BaseModel):
    access_token: str
    token_type: str
