from typing import Dict, List

from mirumon.domain.users.entities import AccessToken, RawPassword, Username
from mirumon.domain.users.scopes import Scopes
from mirumon.infra.api.api_model import APIModel


class UserInLoginRequest(APIModel):
    username: Username
    password: RawPassword
    scopes: List[Scopes]

    @property
    def fields_to_jwt(self) -> Dict[str, str]:
        return self.dict(include={"username", "scopes"})


class UserTokenInResponse(APIModel):
    access_token: AccessToken
    token_type: str
