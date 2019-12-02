from typing import List

from pydantic import BaseModel

from app.models.domain.scopes import Scopes
from app.models.mixins import DateTimeModelMixin, IDModelMixin
from app.services import security


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
