import pytest
from fastapi import FastAPI

pytestmark = [pytest.mark.asyncio, pytest.mark.skip]


async def test_device_registration_success(app: FastAPI, client, shared_key) -> None:
    payload = {"shared_key": shared_key}
    url = app.url_path_for("devices:registration")
    response = await client.post(url, json=payload)
    assert response.status_code == 202
    # TODO fake device service to generate token and id
    assert response.json() == {"device_id": None, "device_token": None}


async def test_device_registration_with_invalid_shared_key(
    app: FastAPI, client
) -> None:
    payload = {"shared_key": "not-secret"}
    url = app.url_path_for("devices:registration")
    response = await client.post(url, json=payload)
    assert response.status_code == 401
    assert response.json() == {"detail": "invalid shared key"}
