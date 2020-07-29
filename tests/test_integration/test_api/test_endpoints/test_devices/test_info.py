import time
import uuid

import pytest
from fastapi import FastAPI

pytestmark = [pytest.mark.asyncio]


async def test_device_detail_event(app: FastAPI, client, device_factory):
    async with device_factory() as device:
        url = app.url_path_for("devices:detail", device_id=device.id)
        response = await client.get(url)
        assert response.status_code == 200
        assert response.json() == {
            "id": device.id,
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
                    "install_date": "2020-07-26T00:32:16.944988",
                },
            ],
            "last_user": {
                "name": "nick",
                "fullname": "Nick Khitrov",
                "domain": "mirumon.dev",
            },
        }


async def test_devices_list_with_two_devices(app, client, device_factory) -> None:
    async with device_factory() as device:
        async with device_factory() as device2:
            url = app.url_path_for("devices:list")
            response = await client.get(url)
            assert response.status_code == 200
            assert response.json() == [
                {
                    "id": device.id,
                    "online": True,
                    "name": "Manjaro-Desktop",
                    "domain": "mirumon.dev",
                    "workgroup": None,
                    "last_user": {
                        "name": "nick",
                        "fullname": "Nick Khitrov",
                        "domain": "mirumon.dev",
                    },
                },
                {
                    "id": device2.id,
                    "online": True,
                    "name": "Manjaro-Desktop",
                    "domain": "mirumon.dev",
                    "workgroup": None,
                    "last_user": {
                        "name": "nick",
                        "fullname": "Nick Khitrov",
                        "domain": "mirumon.dev",
                    },
                },
            ]


async def test_devices_list_without_registered_devices(app, client):
    url = app.url_path_for("devices:list")
    response = await client.get(url)
    assert response.status_code == 200
    assert response.json() == []


async def test_device_not_found(app, client):
    url = app.url_path_for("devices:detail", device_id=uuid.uuid4())
    response = await client.get(url)
    assert response.status_code == 404
    assert response.json() == {"detail": "device not found"}


async def test_device_unavailable_with_bad_payload(app, client, device_factory):
    async with device_factory(response_payload={"bad": "payload"}) as device:
        url = app.url_path_for("devices:detail", device_id=device.id)
        start = time.monotonic()
        response = await client.get(url)
        response_time = time.monotonic() - start
        assert response.status_code == 503
        assert response.json() == {"detail": "device unavailable"}
        assert response_time <= 5 + 0.5  # default for event repo + offset for test
