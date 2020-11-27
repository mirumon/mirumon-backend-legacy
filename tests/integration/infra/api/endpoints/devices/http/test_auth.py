import pytest
from async_asgi_testclient import TestClient
from fastapi import FastAPI

from mirumon.domain.devices.entities import DeviceID
from tests.integration.support.jwt import decode_jwt_token

pytestmark = [pytest.mark.asyncio]


async def test_create_device_without_token(
    app: FastAPI, client: TestClient, shared_key
) -> None:
    payload = {"shared_key": shared_key}
    url = app.url_path_for("devices:create")

    bad_auth_header = {"Authorization": f"Bearer wf4oi1233123123wefw"}
    response = await client.post(url, headers=bad_auth_header, json=payload)
    assert response.status_code == 403
    assert response.json() == {"detail": "could not validate credentials"}


async def test_create_device(app: FastAPI, client, secret_key) -> None:
    url = app.url_path_for("devices:create")

    response = await client.post(url)
    assert response.status_code == 201

    token = response.json()["token"]
    content = decode_jwt_token(token, secret_key)

    assert DeviceID(content["device"]["id"])
    assert response.json() == {"token": token}


async def test_create_device_by_shared_key(
    app: FastAPI, client, shared_key, secret_key
) -> None:
    payload = {"shared_key": shared_key}
    url = app.url_path_for("devices:create-by-shared")

    response = await client.post(url, json=payload)
    assert response.status_code == 201

    token = response.json()["token"]
    content = decode_jwt_token(token, secret_key)

    assert DeviceID(content["device"]["id"])
    assert response.json() == {"token": token}


async def test_device_registration_with_invalid_shared_key_failed(
    app: FastAPI, client
) -> None:
    payload = {"shared_key": "not-secret"}
    url = app.url_path_for("devices:create-by-shared")

    response = await client.post(url, json=payload)

    assert response.status_code == 400
    assert response.json() == {"detail": "invalid shared key"}
