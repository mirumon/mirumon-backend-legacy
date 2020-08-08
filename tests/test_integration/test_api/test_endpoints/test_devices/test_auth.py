import pytest
from fastapi import FastAPI

from app.domain.device.typing import DeviceID
from tests.test_integration.support import decode_jwt_token

pytestmark = [pytest.mark.asyncio]


async def test_device_registration_success(
    app: FastAPI, client, shared_key, secret_key
) -> None:
    payload = {"shared_key": shared_key}
    url = app.url_path_for("devices:registration")

    response = await client.post(url, json=payload)
    assert response.status_code == 201

    resp_payload: dict = response.json()
    assert len(resp_payload) == 1

    content = decode_jwt_token(resp_payload["token"], secret_key)
    # TODO: check id from db when move device storage from redis to postgres
    assert DeviceID(content["device_id"])


async def test_device_registration_with_invalid_shared_key_failed(
    app: FastAPI, client
) -> None:
    payload = {"shared_key": "not-secret"}
    url = app.url_path_for("devices:registration")

    response = await client.post(url, json=payload)

    assert response.status_code == 401
    assert response.json() == {"detail": "invalid shared key"}
