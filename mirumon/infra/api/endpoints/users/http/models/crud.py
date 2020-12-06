from typing import List

from mirumon.domain.users.entities import RawPassword, UserID, Username
from mirumon.domain.users.scopes import Scopes
from mirumon.infra.api.api_model import APIModel


class UserInCreateRequest(APIModel):
    username: Username
    password: RawPassword
    scopes: List[Scopes]


class UserInCreateResponse(APIModel):
    id: UserID
    username: Username
    scopes: List[Scopes]
