import pytest
from fastapi import FastAPI

pytestmark = [pytest.mark.asyncio]


async def test_device_registration_success(app: FastAPI, client, shared_key) -> None:
    payload = {"shared_key": shared_key}
    url = app.url_path_for("devices:registration")
    response = await client.post(url, json=payload)
    assert response.status_code == 201
    # TODO fake device service to generate token and id
    resp_payload = response.json()
    assert resp_payload["device_id"]
    assert resp_payload["device_token"]


async def test_device_registration_with_invalid_shared_key_failed(
    app: FastAPI, client
) -> None:
    payload = {"shared_key": "not-secret"}
    url = app.url_path_for("devices:registration")
    response = await client.post(url, json=payload)
    assert response.status_code == 401
    assert response.json() == {"detail": "invalid shared key"}
