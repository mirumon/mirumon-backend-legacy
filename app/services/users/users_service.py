from datetime import timedelta
from typing import List

from asyncpg import UniqueViolationError
from fastapi.security import SecurityScopes

from app.components import jwt
from app.components.config import APPSettings
from app.database.errors import EntityDoesNotExist
from app.database.repositories.users_repo import UsersRepository
from app.domain.user.scopes import Scopes
from app.domain.user.user import Token, User, UserInLogin, UserInCreate, UserInDB


class UsersService:
    users_repo: UsersRepository
    secret_key: str
    jwt_token_type: str

    def __init__(
        self, users_repo: UsersRepository, settings: APPSettings,
    ):
        self.users_repo = users_repo
        self.settings = settings
        self.jwt_token_type = settings.jwt_token_type
        self.access_token_expire = timedelta(weeks=1)

    async def register_new_user(self, user: UserInCreate) -> User:
        try:
            return await self.users_repo.create_user(**user.dict())
        except UniqueViolationError:  # todo add exception type
            raise RuntimeError("username is already exists")

    async def login_user(self, user: UserInLogin) -> Token:
        if not await self.users_repo.check_user_credentials(user):
            raise RuntimeError("incorrect user credentials")

        token = jwt.create_jwt_token(
            jwt_content=user.dict(),
            secret_key=str(self.settings.secret_key),
            expires_delta=self.access_token_expire,
        )
        return Token(access_token=token, token_type=self.jwt_token_type)

    async def find_user_by_token(self, token: str, secret_key: str) -> UserInDB:
        try:
            stored_user = jwt.get_user_from_token(token, secret_key)
        except ValueError:
            raise RuntimeError("token decode error")

        try:
            return await self.users_repo.get_user_by_username(
                username=stored_user.username
            )
        except EntityDoesNotExist:
            raise RuntimeError("user does not exist")

    def check_user_scopes(self, scopes: List[Scopes], security_scopes: SecurityScopes):
        return not all(scope in scopes for scope in security_scopes.scopes)
