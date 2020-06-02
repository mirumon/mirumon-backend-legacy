from typing import Callable, List

from fastapi import Depends, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from starlette import status

from app.db import UsersRepository
from app.db.errors import EntityDoesNotExist
from old_app.api.dependencies.database import get_repository
from old_app.common import strings
from app.settings.environments.config import SECRET_KEY
from old_app.models.domain.scopes import AdministrationScopes, UserScopes
from old_app.models.domain.users import User
from old_app.services import jwt

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
    users_repo: UsersRepository = Depends(get_repository(UsersRepository)),
) -> User:
    try:
        stored_user = jwt.get_user_from_token(token, str(SECRET_KEY))
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=strings.MALFORMED_PAYLOAD
        )

    try:
        user = await users_repo.get_user_by_username(username=stored_user.username)
    except EntityDoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=strings.MALFORMED_PAYLOAD
        )

    if not all(scope in user.scopes for scope in security_scopes.scopes):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=strings.NOT_ENOUGH_PRIVILEGES
        )

    return user


def get_current_user(user: User = Security(_get_current_user)) -> User:
    return user


def check_user_scopes_requirements(required_scopes: List[str]) -> Callable:
    def _check_scopes(
        user: User = Security(get_current_user, scopes=required_scopes)
    ) -> User:
        return user

    return _check_scopes
