from datetime import datetime, timedelta
from typing import Dict

import bcrypt
import jwt
from loguru import logger
from passlib.context import CryptContext
from pydantic import BaseModel

from app.domain.user.user import HashedPassword


class MetaJWT(BaseModel):
    exp: datetime
    sub: str


class AuthService:
    JWT_SUBJECT = "access"
    ALGORITHM = "HS256"
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def create_jwt_token(
        self, *, jwt_content: Dict[str, str], secret_key: str, expires_delta: timedelta,
    ) -> str:
        to_encode = jwt_content.copy()
        expire = datetime.utcnow() + expires_delta
        to_encode.update(MetaJWT(exp=expire, sub=self.JWT_SUBJECT).dict())
        return jwt.encode(to_encode, secret_key, algorithm=self.ALGORITHM).decode()

    def get_content_from_token(self, token: str, secret_key: str) -> Dict[str, str]:
        try:
            return jwt.decode(token, secret_key, algorithms=[self.ALGORITHM])
        except jwt.PyJWTError as decode_error:
            logger.debug("jwt decode error")
            raise ValueError("unable to decode JWT token") from decode_error

    def generate_salt(self) -> str:
        return bcrypt.gensalt().decode()

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> HashedPassword:
        return HashedPassword(self.pwd_context.hash(password))
