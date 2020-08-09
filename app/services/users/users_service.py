from datetime import timedelta
from typing import List

from asyncpg import UniqueViolationError
from fastapi.security import SecurityScopes
from loguru import logger
from pydantic import ValidationError

from app.api.models.http.users import UserInCreate, UserInLogin, UserToken
from app.database.errors import EntityDoesNotExist
from app.database.repositories.users_repo import UsersRepository
from app.domain.user.scopes import Scopes
from app.domain.user.user import (
    AccessToken,
    HashedPassword,
    RawPassword,
    User,
    UserInDB,
    UserJWT,
)
from app.services.authentication.base_auth_service import AuthService
from app.settings.environments.base import AppSettings


class UsersService(AuthService):
    def __init__(
        self, users_repo: UsersRepository, settings: AppSettings,
    ):
        self.users_repo = users_repo
        self.settings = settings
        self.jwt_token_type = settings.jwt_token_type
        # todo: move to settings
        self.access_token_expire = timedelta(weeks=1)

    async def register_new_user(self, user: UserInCreate) -> User:
        salt = self.generate_salt()
        hashed_password = self.get_password_hash(salt + str(user.password))
        try:
            return await self.users_repo.create_user(
                username=user.username,
                salt=salt,
                password=hashed_password,
                scopes=user.scopes,
            )
        except UniqueViolationError:  # todo add exception type
            raise RuntimeError("username is already exists")

    async def login_user(self, user: UserInLogin) -> UserToken:
        if not await self.check_user_credentials(user):
            raise RuntimeError("incorrect user credentials")

        try:
            jwt_user = UserJWT(**user.dict())
        except ValidationError as error:
            logger.debug(f"jwt user invalid:{error.errors()}")
            raise RuntimeError

        token = self.create_jwt_token(
            jwt_content=jwt_user.dict(),
            secret_key=self.settings.secret_key.get_secret_value(),
            expires_delta=self.access_token_expire,
        )
        return UserToken(
            access_token=AccessToken(token), token_type=self.jwt_token_type
        )

    async def find_user_by_token(self, token: str, secret_key: str) -> UserInDB:
        try:
            logger.debug(f"secret:{secret_key}\ttoken:{token}")
            payload = self.get_content_from_token(token, secret_key)
        except ValueError:
            logger.debug("token decode error")
            raise RuntimeError("token decode error")

        try:
            user = UserJWT(**payload)  # type: ignore
        except ValidationError as validation_error:
            logger.debug(f"validation error:{validation_error.errors()}")
            raise RuntimeError("malformed payload in token") from validation_error

        try:
            return await self.users_repo.get_user_by_username(username=user.username)
        except EntityDoesNotExist:
            logger.debug("user does not exist")
            raise RuntimeError("user does not exist")

    async def check_user_credentials(self, user: UserInLogin) -> bool:
        try:
            user_db = await self.users_repo.get_user_by_username(username=user.username)
        except EntityDoesNotExist:
            return False
        return self.verify_password(
            user_db.salt + str(user.password), user_db.hashed_password,
        )

    def check_user_scopes(
        self, scopes: List[Scopes], security_scopes: SecurityScopes
    ) -> bool:
        # todo: add is active check
        return not all(scope in scopes for scope in security_scopes.scopes)

    def change_user_password(self, user: UserInDB, password: RawPassword) -> None:
        user.salt = self.generate_salt()
        hashed_password = self.get_password_hash(user.salt + str(password))
        user.hashed_password = HashedPassword(hashed_password)
