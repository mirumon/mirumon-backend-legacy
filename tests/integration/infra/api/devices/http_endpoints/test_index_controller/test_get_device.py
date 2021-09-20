import uuid

import pytest
from fastapi import FastAPI

pytestmark = [pytest.mark.asyncio]


@pytest.fixture
def device_id():
    return str(uuid.uuid4())


@pytest.fixture
async def response(app: FastAPI, client, device_id, device_factory):
    async with device_factory(device_id=device_id) as device:
        url = app.url_path_for("devices:get", device_id=device.id)
        response = await client.get(url)
        return response


async def test_should_return_expected_response(response, device_id):
    assert response.status_code == 200
    assert response.json() == {
        "id": device_id,
        "online": True,
        "name": f"Device-{device_id}",
    }


async def test_device_available_with_bad_payload(app, client, device_factory):
    async with device_factory(response_payload={"bad": "payload"}) as device:
        url = app.url_path_for("devices:get", device_id=device.id)
        response = await client.get(url)
        assert response.status_code == 200
        assert response.json() == {
            "id": str(device.id),
            "online": True,
            "name": f"Device-{device.id}",
        }
