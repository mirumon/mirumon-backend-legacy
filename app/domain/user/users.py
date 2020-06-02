from datetime import datetime
from typing import List

from pydantic import BaseModel

from app.domain.mixins import DateTimeModelMixin, IDModelMixin
from old_app.models.domain.scopes import Scopes
from old_app.services import security


class User(BaseModel):
    username: str
    scopes: List[Scopes]


class UserInDB(IDModelMixin, DateTimeModelMixin, User):
    salt: str = ""
    hashed_password: str = ""

    def check_password(self, password: str) -> bool:
        return security.verify_password(self.salt + password, self.hashed_password)

    def change_password(self, password: str) -> None:
        self.salt = security.generate_salt()
        self.hashed_password = security.get_password_hash(self.salt + password)


class JWTMeta(BaseModel):
    exp: datetime
    sub: str


class JWTUser(BaseModel):
    username: str
    scopes: List[Scopes]


class JWTToken(BaseModel):
    access_token: str
    token_type: str
