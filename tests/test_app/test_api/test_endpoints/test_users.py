from datetime import timedelta

import pytest
from async_asgi_testclient import TestClient

from app.settings.components import jwt

pytestmark = [pytest.mark.asyncio]


@pytest.fixture
def superuser_username() -> str:
    return "test-superuser-username"


@pytest.fixture
def superuser_password() -> str:
    return "test-superuser-password"


@pytest.fixture
def secret_key() -> str:
    return "test-secret-key"


@pytest.fixture
def admin(superuser_username: str, superuser_password: str):
    return {"username": superuser_username, "password": superuser_password}


@pytest.fixture
def token(admin, secret_key):
    return jwt.create_jwt_token(
        jwt_content=admin, secret_key=secret_key, expires_delta=timedelta(minutes=1),
    )


@pytest.fixture
def token_header(token):
    return {"Authorization": f"Bearer {token}"}


async def test_first_superuser_login_success(client: TestClient, admin) -> None:
    url = client.application.url_path_for("auth:login")
    response = await client.post(url, form=admin)
    assert response.status_code == 200

    # TODO add test with fake users service to check token
    resp_payload = response.json()
    assert resp_payload["access_token"]
    assert resp_payload["token_type"] == "Bearer"


async def test_first_superuser_login_failed(client: TestClient) -> None:
    url = client.application.url_path_for("auth:login")
    response = await client.post(url, form={"username": "admin", "password": "admin"})
    assert response.status_code == 400
    assert response.json() == {"detail": "incorrect login or password"}


async def test_first_superuser_create_new_user_with_empty_scopes_success(
    client: TestClient, token_header
) -> None:
    url = client.application.url_path_for("auth:register")
    new_user = {
        "username": "test-new-user",
        "password": "test-new-user-password",
        "scopes": [],
    }
    response = await client.post(url, headers=token_header, json=new_user)
    assert response.status_code == 201
    resp_payload = response.json()
    assert resp_payload["username"] == new_user["username"]
    assert resp_payload["id"]
    assert resp_payload["scopes"] == []


async def test_first_superuser_create_new_user_with_same_username_failed(
    client: TestClient, token_header, admin
) -> None:
    url = client.application.url_path_for("auth:register")
    new_user = admin
    response = await client.post(url, headers=token_header, json=new_user)
    assert response.status_code == 400
    assert response.json() == {"detail": "user with this username already exists"}
