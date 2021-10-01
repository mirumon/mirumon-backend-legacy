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


async def test_first_superuser_login_success(client: TestClient, user) -> None:
    url = client.application.url_path_for("users:token")
    response = await client.post(url, form=user)
    assert response.status_code == 200

    # TODO decode token to check user payload
    # TODO check user in db
    resp_payload = response.json()
    assert resp_payload["access_token"]
    assert resp_payload["token_type"] == "Bearer"


async def test_first_superuser_login_failed(client: TestClient) -> None:
    url = client.application.url_path_for("users:token")
    response = await client.post(url, form={"username": "admin", "password": "admin"})
    assert response.status_code == 400
    assert response.json() == {"detail": "incorrect login or password or scopes"}
