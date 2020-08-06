from datetime import timedelta

from app.api.models.http.users import UserInLogin
from app.settings.components import jwt


def test_user_jwt_decoding(secret_key):
    # todo
    user = UserInLogin(username="testuser", password="pass")
    token = jwt.create_jwt_token(
        jwt_content=user.dict(), secret_key=secret_key, expires_delta=timedelta(weeks=1)
    )
    content = jwt.get_content_from_token(token, secret_key)
    assert content["username"] == user.username
    assert content["password"] == user.password
