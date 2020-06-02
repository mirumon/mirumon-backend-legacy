from typing import List, NewType
from uuid import UUID

from app.components.core import APIModel
from app.domain.user.scopes import Scopes

UserUID = NewType("UserUID", UUID)


class User(APIModel):
    id: UserUID
    username: str
    scopes: List[Scopes]


class UserInDB(User):
    salt: str = ""
    hashed_password: str = ""
