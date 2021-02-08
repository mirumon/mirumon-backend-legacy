from datetime import datetime, timedelta
from typing import Dict, Final, List

import bcrypt
from fastapi.security import SecurityScopes
from jose import jwt
from loguru import logger
from passlib.context import CryptContext
from pydantic import BaseModel, SecretStr, ValidationError

from mirumon.application.users.users_service import UsersService
from mirumon.domain.users.entities import (
    AccessToken,
    HashedPassword,
    RawPassword,
    User,
    Username,
)
from mirumon.domain.users.scopes import Scopes


class MetaJWT(BaseModel):
    exp: datetime
    sub: str


class UserJWT(BaseModel):
    username: Username
    scopes: List[Scopes]


class AuthUsersService:  # noqa: WPS214
    jwt_token_type: Final = "Bearer"
    jwt_subject: Final = "access"
    algorithm: Final = "HS256"
    pwd_context: Final = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def __init__(
        self,
        users_service: UsersService,
        secret_key: SecretStr,
        access_token_expire: timedelta,
    ):
        self.users_service = users_service
        self.access_token_expire = access_token_expire
        self.secret_key = secret_key

    async def register_new_user(
        self, username: Username, password: RawPassword, scopes: Scopes
    ) -> User:
        salt = _generate_salt()
        hashed_password = self._get_password_hash(salt, password)

        return await self.users_service.create_new_user(
            username=username,
            scopes=scopes,
            salt=salt,
            hashed_password=hashed_password,
        )

    async def create_access_token(
        self, username: Username, raw_password: RawPassword, scopes: Scopes
    ) -> Dict[str, str]:
        if not await self._check_user_credentials(username, raw_password):
            raise RuntimeError("incorrect user credentials")

        token = self._create_jwt_token(
            jwt_content={"username": username, "scopes": scopes},
            secret_key=self.secret_key.get_secret_value(),
            expires_delta=self.access_token_expire,
        )
        return {"access_token": token, "token_type": self.jwt_token_type}

    async def find_user_by_token(self, token: AccessToken) -> User:
        try:
            payload = self._get_content_from_token(
                token, self.secret_key.get_secret_value()
            )
        except ValueError:
            logger.debug("token decode error")
            raise RuntimeError("token decode error")

        try:
            user = UserJWT.parse_obj(payload)
        except ValidationError as validation_error:
            logger.debug(f"validation error:{validation_error.errors()}")
            raise RuntimeError("malformed payload in token")

        return await self.users_service.find_user_by_username(username=user.username)

    def check_user_scopes(
        self, scopes: List[Scopes], security_scopes: SecurityScopes
    ) -> bool:
        # todo: add is_active check
        return not all(scope in scopes for scope in security_scopes.scopes)

    async def _check_user_credentials(
        self, username: Username, raw_password: RawPassword
    ) -> bool:
        try:
            user_db = await self.users_service.find_user_by_username(username=username)
        except RuntimeError:
            return False
        return self._verify_password(
            user_db.salt,
            raw_password,
            user_db.hashed_password,
        )

    def _create_jwt_token(
        self, *, jwt_content: Dict[str, str], secret_key: str, expires_delta: timedelta
    ) -> AccessToken:
        to_encode = jwt_content.copy()
        expire = datetime.utcnow() + expires_delta
        to_encode.update(MetaJWT(exp=expire, sub=self.jwt_subject).dict())
        token = jwt.encode(to_encode, secret_key, algorithm=self.algorithm)
        return AccessToken(token)

    def _get_content_from_token(
        self, token: AccessToken, secret_key: str
    ) -> Dict[str, str]:
        try:
            return jwt.decode(token, secret_key, algorithms=[self.algorithm])
        except jwt.JWTError as decode_error:
            logger.debug("jwt decode error")
            raise ValueError("unable to decode JWT token") from decode_error

    def _verify_password(
        self, salt: str, raw_password: RawPassword, hashed_password: str
    ) -> bool:
        plain_password_with_salt = salt + str(raw_password)
        return self.pwd_context.verify(plain_password_with_salt, hashed_password)

    def _get_password_hash(self, salt: str, password: RawPassword) -> HashedPassword:
        return HashedPassword(self.pwd_context.hash(salt + str(password)))


def _generate_salt() -> str:
    return bcrypt.gensalt().decode()
