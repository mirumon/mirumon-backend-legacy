from fastapi import Depends

from mirumon.api.dependencies.repositories import get_repository
from mirumon.application.users.auth_service import AuthUsersService
from mirumon.application.users.users_repo import UserRepository
from mirumon.application.users.users_service import UserService
from mirumon.settings.config import get_app_settings
from mirumon.settings.environments.app import AppSettings


def _get_users_service(
    users_repository: UserRepository = Depends(get_repository(UserRepository)),
) -> UserService:
    return UserService(users_repo=users_repository)


def get_auth_users_service(
    users_service: UserService = Depends(_get_users_service),
    settings: AppSettings = Depends(get_app_settings),
) -> AuthUsersService:
    return AuthUsersService(
        users_service=users_service,
        secret_key=settings.secret_key,
        access_token_expire=settings.access_token_expire,
    )
