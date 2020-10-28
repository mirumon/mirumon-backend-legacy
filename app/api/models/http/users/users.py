from typing import Dict, List, Optional

from app.api.models.base import APIModel
from app.domain.users.scopes import Scopes
from app.domain.users.user import AccessToken, RawPassword, UserID, Username


class User(APIModel):
    id: UserID
    username: Username
    scopes: List[Scopes]


class UserInCreate(APIModel):
    username: Username
    password: RawPassword
    scopes: List[Scopes]


class UserInUpdate(APIModel):
    username: Optional[Username] = None
    password: Optional[RawPassword] = None
    scopes: List[Scopes] = []


class UserInLogin(APIModel):
    username: Username
    password: RawPassword
    scopes: List[Scopes]

    @property
    def fields_to_jwt(self) -> Dict[str, str]:
        return self.dict(include={"username", "scopes"})


class UserToken(APIModel):
    access_token: AccessToken
    token_type: str
