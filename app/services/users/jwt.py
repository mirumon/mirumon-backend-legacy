from datetime import datetime, timedelta
from typing import Dict

import jwt
from pydantic import ValidationError

from app.domain.user.jwt import JWTMeta, User
from app.domain.user.user import User

JWT_SUBJECT = "access"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE = timedelta(weeks=1)


def _create_jwt_token(
    *, jwt_content: Dict[str, str], secret_key: str, expires_delta: timedelta
) -> str:
    to_encode = jwt_content.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update(JWTMeta(exp=expire, sub=JWT_SUBJECT).dict())
    return jwt.encode(to_encode, secret_key, algorithm=ALGORITHM).decode()


def create_access_token_for_user(user: User, secret_key: str) -> str:
    return _create_jwt_token(
        jwt_content=User(username=user.username, scopes=user.scopes).dict(),
        secret_key=secret_key,
        expires_delta=ACCESS_TOKEN_EXPIRE,
    )


def get_user_from_token(token: str, secret_key: str) -> User:
    try:
        user_from_jwt = jwt.decode(token, secret_key, algorithms=[ALGORITHM])
    except jwt.PyJWTError as decode_error:
        raise ValueError("unable to decode JWT token") from decode_error

    try:
        return User(**user_from_jwt)
    except ValidationError as validation_error:
        raise ValueError("malformed payload in token") from validation_error
