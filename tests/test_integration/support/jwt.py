from datetime import datetime, timedelta

from jose import jwt


def create_jwt_token(
    jwt_content: dict,
    secret_key: str,
    expires_delta: timedelta,
) -> str:
    to_encode = jwt_content.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update(dict(exp=expire, sub="access"))
    return jwt.encode(to_encode, secret_key, algorithm="HS256")


def decode_jwt_token(token: str, secret_key: str):
    return jwt.decode(token, secret_key, algorithms=["HS256"])
