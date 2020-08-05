from datetime import datetime, timedelta
from typing import Dict

import bcrypt
import jwt
from loguru import logger
from passlib.context import CryptContext

from app.domain.user.user import MetaJWT

JWT_SUBJECT = "access"
ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_jwt_token(
    *, jwt_content: Dict[str, str], secret_key: str, expires_delta: timedelta,
) -> str:
    to_encode = jwt_content.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update(MetaJWT(exp=expire, sub=JWT_SUBJECT).dict())
    return jwt.encode(to_encode, secret_key, algorithm=ALGORITHM).decode()


def get_content_from_token(token: str, secret_key: str) -> Dict[str, str]:
    try:
        return jwt.decode(token, secret_key, algorithms=[ALGORITHM])
    except jwt.PyJWTError as decode_error:
        logger.debug("jwt decode error")
        raise ValueError("unable to decode JWT token") from decode_error


def generate_salt() -> str:
    return bcrypt.gensalt().decode()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
