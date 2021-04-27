import uuid

import pytest
from fastapi import FastAPI

pytestmark = [pytest.mark.asyncio]


@pytest.fixture
async def response(app: FastAPI, client, device_factory):
    async with device_factory(device_id=str(uuid.uuid4())) as device:
        url = app.url_path_for("devices:software", device_id=device.id)
        response = await client.get(url)
        return response


async def test_should_return_response_with_software_list(response):
    assert response.status_code == 200
    assert response.json() == [
        {"name": "7zip", "vendor": "7zip", "version": "1.0.0"},
        {"name": "Python3.8", "vendor": "python", "version": "3.8.0"},
    ]
