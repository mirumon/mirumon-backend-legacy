from datetime import timedelta
from typing import List

from asyncpg import UniqueViolationError
from fastapi.security import SecurityScopes
from pydantic import ValidationError

from app.database.errors import EntityDoesNotExist
from app.database.repositories.users_repo import UsersRepository
from app.domain.user.scopes import Scopes
from app.domain.user.user import UserToken, User, UserInCreate, UserInDB, UserInLogin, \
    UserJWT
from app.settings.components import jwt
from app.settings.components.logger import logger
from app.settings.environments.base import AppSettings


class UsersService:
    users_repo: UsersRepository
    secret_key: str
    jwt_token_type: str

    def __init__(
        self, users_repo: UsersRepository, settings: AppSettings,
    ):
        self.users_repo = users_repo
        self.settings = settings
        self.jwt_token_type = settings.jwt_token_type
        # todo: move to settings
        self.access_token_expire = timedelta(weeks=1)

    async def register_new_user(self, user: UserInCreate) -> User:
        try:
            return await self.users_repo.create_user(**user.dict())
        except UniqueViolationError:  # todo add exception type
            raise RuntimeError("username is already exists")

    async def login_user(self, user: UserInLogin) -> UserToken:
        if not await self.users_repo.check_user_credentials(user):
            raise RuntimeError("incorrect user credentials")

        try:
            jwt_user = UserJWT(**user.dict())
        except ValidationError as error:
            logger.debug(f"jwt user invalid:{error.errors()}")
            raise RuntimeError

        token = jwt.create_jwt_token(
            jwt_content=jwt_user.dict(),
            secret_key=self.settings.secret_key.get_secret_value(),
            expires_delta=self.access_token_expire,
        )
        return UserToken(access_token=token, token_type=self.jwt_token_type)

    async def find_user_by_token(self, token: str, secret_key: str) -> UserInDB:
        try:
            logger.debug(f"secret:{secret_key}\ttoken:{token}")
            stored_user = jwt.get_user_from_token(token, secret_key)
        except ValueError:
            logger.debug("token decode error")
            raise RuntimeError("token decode error")

        try:
            return await self.users_repo.get_user_by_username(
                username=stored_user.username,
            )
        except EntityDoesNotExist:
            logger.debug("user does not exist")
            raise RuntimeError("user does not exist")

    def check_user_scopes(self, scopes: List[Scopes], security_scopes: SecurityScopes):
        return not all(scope in scopes for scope in security_scopes.scopes)
