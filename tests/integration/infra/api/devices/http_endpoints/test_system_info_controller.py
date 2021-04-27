import time
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
        url = app.url_path_for("devices:detail", device_id=device.id)
        response = await client.get(url)
        return response


async def test_should_return_expected_response(response, device_id):
    assert response.status_code == 200
    assert response.json() == {
        "id": device_id,
        "online": True,
        "name": "Manjaro-Desktop",
        "domain": "mirumon.dev",
        "workgroup": None,
        "os": [
            {
                "name": "Windows 10 Edu",
                "version": "1.12.12",
                "os_architecture": "amd64",
                "serial_number": "AGFNE-34GS-RYHRE",
                "number_of_users": 4,
            }
        ],
        "last_user": {
            "name": "nick",
            "fullname": "Nick Khitrov",
            "domain": "mirumon.dev",
        },
    }


async def test_device_unavailable_with_bad_payload(app, client, device_factory):
    async with device_factory(response_payload={"bad": "payload"}) as device:
        url = app.url_path_for("devices:detail", device_id=device.id)
        start = time.monotonic()
        response = await client.get(url)
        response_time = time.monotonic() - start
        assert response.status_code == 504
        assert response.json() == {"detail": "device unavailable"}
        assert response_time <= 5 + 0.5  # default for event repo + offset for test
