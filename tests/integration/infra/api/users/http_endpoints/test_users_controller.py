import pytest
from async_asgi_testclient import TestClient

from mirumon.domain.users.scopes import DevicesScopes

pytestmark = [pytest.mark.asyncio]


@pytest.fixture
def user(superuser_username, superuser_password):
    return {
        "username": superuser_username,
        "password": superuser_password,
        "scopes": [DevicesScopes.read],
    }


async def test_first_superuser_create_new_user_with_empty_scopes_success(
    client: TestClient, token_header
) -> None:
    url = client.application.url_path_for("users:create")
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
    client: TestClient, token_header, user
) -> None:
    url = client.application.url_path_for("users:create")
    new_user = user
    response = await client.post(url, headers=token_header, json=new_user)
    assert response.status_code == 400
    assert response.json() == {"detail": "user with this username already exists"}
