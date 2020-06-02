from datetime import datetime
from typing import List

from pydantic import BaseModel

from old_app.models.domain.scopes import Scopes


class JWTMeta(BaseModel):
    exp: datetime
    sub: str


class JWTUser(BaseModel):
    username: str
    scopes: List[Scopes]


class JWTToken(BaseModel):
    access_token: str
    token_type: str
