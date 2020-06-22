import pytest
from async_asgi_testclient import TestClient
from fastapi import FastAPI

pytestmark = [pytest.mark.asyncio]


@pytest.fixture
def superuser_username() -> str:
    return "test-superuser-username"


@pytest.fixture
def superuser_password() -> str:
    return "test-superuser-password"


async def test_first_superuser_login_success(
   client: TestClient, superuser_username: str, superuser_password: str, printer
) -> None:
    payload = {"username": superuser_username, "password": superuser_password}
    url = client.application.url_path_for("auth:login")
    response = await client.post(url,  files=payload)
    data = response.json()
    printer(data)
    assert response.status_code == 201

    assert data["access_token"]
    assert data["token_type"] == "Bearer"
