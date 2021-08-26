from typing import Callable, List

from fastapi import Depends, HTTPException, Security
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
    SecurityScopes,
)
from starlette import status

from mirumon.application.users.auth_service import AuthUsersService
from mirumon.domain.users.entities import AccessToken, RawPassword, User, Username
from mirumon.domain.users.scopes import DevicesScopes, UsersScopes
from mirumon.api.dependencies.services import get_service
from mirumon.api.users.http_endpoints.models.auth import UserInLoginRequest
from mirumon.resources import strings

oauth2_schema = OAuth2PasswordBearer(
    tokenUrl="/users/token",
    scopes={
        DevicesScopes.read: "Retrieve information about devices",
        DevicesScopes.write: "Register devices and run shell commands on devices",
        UsersScopes.read: "View information about users",
        UsersScopes.write: "Create users and edit information about users",
    },
)


async def _get_current_user(
    security_scopes: SecurityScopes,
    token: AccessToken = Depends(oauth2_schema),
    users_service: AuthUsersService = Depends(get_service(AuthUsersService)),
) -> User:
    try:
        user = await users_service.find_user_by_token(token=token)
    except RuntimeError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=strings.MALFORMED_PAYLOAD,
        )

    if users_service.check_user_scopes(user.scopes, security_scopes):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=strings.NOT_ENOUGH_PRIVILEGES,
        )

    return user


def get_current_user(user: User = Security(_get_current_user)) -> User:
    return user


def check_user_scopes(required_scopes: List[str]) -> Callable[[User], User]:
    def _check_scopes(
        user: User = Security(get_current_user, scopes=required_scopes),
    ) -> User:
        return user

    return _check_scopes


def get_user_in_login(
    user: OAuth2PasswordRequestForm = Depends(),
) -> UserInLoginRequest:
    return UserInLoginRequest(
        username=Username(user.username),
        password=RawPassword(user.password),
        scopes=user.scopes,
    )
