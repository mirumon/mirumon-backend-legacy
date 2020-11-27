import time
import uuid

import pytest
from fastapi import FastAPI

pytestmark = [pytest.mark.asyncio]


class BaseTestDevice:
    """Test scenario for http request for one device."""

    url_name = None
    expected_status_code = 200
    expected_return_payload = None

    device_id = "baa81326-9953-4587-92ce-82bb1ca1373c"
    pytestmark = pytest.mark.asyncio

    @pytest.fixture
    async def response(self, app: FastAPI, client, device_factory):
        assert self.url_name, "set url_name for test class"
        async with device_factory(device_id=self.device_id) as device:
            url = app.url_path_for(self.url_name, device_id=device.id)
            response = await client.get(url)
            return response

    async def test_should_return_expected_status_code(self, response):
        assert response.status_code == self.expected_status_code

    async def test_should_return_expected_payload(self, response):
        assert response.json() == self.expected_return_payload


class TestDeviceDetail(BaseTestDevice):
    url_name = "devices:detail"
    expected_status_code = 200
    expected_return_payload = {
        "id": "baa81326-9953-4587-92ce-82bb1ca1373c",
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


class TestDeviceSoftware(BaseTestDevice):
    url_name = "devices:software"
    expected_status_code = 200
    expected_return_payload = [
        {"name": "7zip", "vendor": "7zip", "version": "1.0.0"},
        {"name": "Python3.8", "vendor": "python", "version": "3.8.0"},
    ]


class TestDeviceHardware(BaseTestDevice):
    url_name = "devices:hardware"
    expected_status_code = 200
    expected_return_payload = {
        "motherboard": {
            "name": "string",
            "caption": "string",
            "status": "string",
            "product": "string",
            "serial_number": "string",
        },
        "cpu": [
            {
                "status": "string",
                "name": "string",
                "caption": "string",
                "current_clock_speed": "string",
                "current_cthread_countlock_speed": 0,
                "virtualization_firmware_enabled": True,
                "load_percentage": 0,
                "number_of_cores": 0,
                "number_of_enabled_core": 0,
                "number_of_logical_processors": 0,
            }
        ],
        "gpu": [
            {
                "status": "string",
                "name": "string",
                "caption": "string",
                "driver_version": "string",
                "driver_date": "string",
                "video_mode_description": "string",
                "current_vertical_resolution": "string",
            }
        ],
        "network": [
            {
                "description": "string",
                "mac_address": "string",
                "ip_addresses": ["string"],
            }
        ],
        "disks": [
            {
                "status": "string",
                "caption": "string",
                "serial_number": "string",
                "size": 0,
                "model": "string",
                "description": "string",
                "partitions": 0,
            }
        ],
    }


async def test_devices_list_without_registered_devices(app, client):
    url = app.url_path_for("devices:list")
    response = await client.get(url)
    assert response.status_code == 200
    assert response.json() == []


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
                    "os": [
                        {
                            "name": "Windows 10 Edu",
                            "version": "1.12.12",
                            "os_architecture": "amd64",
                            "serial_number": "AGFNE-34GS-RYHRE",
                            "number_of_users": 4,
                        },
                    ],
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
                    "os": [
                        {
                            "name": "Windows 10 Edu",
                            "version": "1.12.12",
                            "os_architecture": "amd64",
                            "serial_number": "AGFNE-34GS-RYHRE",
                            "number_of_users": 4,
                        },
                    ],
                },
            ]


# 4xx and 5xx
async def test_device_not_found(app, client):
    url = app.url_path_for("devices:detail", device_id=str(uuid.uuid4()))
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
