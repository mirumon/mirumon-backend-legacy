from typing import Callable, List

from fastapi import Depends, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer, SecurityScopes, \
    OAuth2PasswordRequestForm
from starlette import status

from app.api.dependencies.services import get_users_service
from app.components.config import APPSettings, get_app_settings
from app.domain.user.scopes import AdministrationScopes, UserScopes
from app.domain.user.user import User, UserInLogin, RawPassword
from app.resources import strings
from app.services.users.users_service import UsersService

oauth2_schema = OAuth2PasswordBearer(
    tokenUrl="/users/login",
    scopes={
        UserScopes.read: "Retrieve information about devices",
        UserScopes.execute: "Run commands on device",
        AdministrationScopes.view: "View information about users or groups",
        AdministrationScopes.edit: "Change information about users or groups",
    },
)


async def _get_current_user(
    security_scopes: SecurityScopes,
    token: str = Depends(oauth2_schema),
    settings: APPSettings = Depends(get_app_settings),
    users_service: UsersService = Depends(get_users_service),
) -> User:
    try:
        user = await users_service.find_user_by_token(
            token=token, secret_key=str(settings.secret_key)
        )
    except RuntimeError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=strings.MALFORMED_PAYLOAD
        )

    if users_service.check_user_scopes(user.scopes, security_scopes):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=strings.NOT_ENOUGH_PRIVILEGES
        )

    return user


def get_current_user(user: User = Security(_get_current_user)) -> User:
    return user


def check_user_scopes(required_scopes: List[str]) -> Callable:
    def _check_scopes(
        user: User = Security(get_current_user, scopes=required_scopes)
    ) -> User:
        return user

    return _check_scopes


def get_user_in_login(user: OAuth2PasswordRequestForm = Depends()) -> UserInLogin:
    return UserInLogin(username=user.username, password=RawPassword(user.password))