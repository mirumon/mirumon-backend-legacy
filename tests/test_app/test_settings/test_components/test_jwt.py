from datetime import timedelta

from app.domain.user.user import UserInLogin
from app.settings.components.jwt import create_jwt_token


def test_user_jwt_decoding(secret_key):
    user = UserInLogin()
    token = create_jwt_token(jwt_content=user.dict(), secret_key=secret_key, expires_delta=timedelta(weeks=1))
