from fastapi import Depends

from mirumon.application.users.auth_service import AuthUsersService
from mirumon.application.users.users_service import UsersService
from mirumon.infra.api.dependencies.repositories import get_repository
from mirumon.infra.users.users_repo import UsersRepository
from mirumon.settings.config import get_app_settings
from mirumon.settings.environments.base import AppSettings


def _get_users_service(
    users_repository: UsersRepository = Depends(get_repository(UsersRepository)),
) -> UsersService:
    return UsersService(users_repo=users_repository)


def get_auth_users_service(
    users_service: UsersService = Depends(_get_users_service),
    settings: AppSettings = Depends(get_app_settings),
) -> AuthUsersService:
    return AuthUsersService(
        users_service=users_service,
        secret_key=settings.secret_key,
        access_token_expire=settings.access_token_expire,
    )
