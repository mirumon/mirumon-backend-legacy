from typing import List

from mirumon.api.api_model import APIModel
from mirumon.domain.users.entities import AccessToken, RawPassword, Username
from mirumon.domain.users.scopes import Scopes


class UserInLoginRequest(APIModel):
    username: Username
    password: RawPassword
    scopes: List[Scopes]


class UserTokenInResponse(APIModel):
    access_token: AccessToken
    token_type: str
