import time
import uuid

import pytest
from fastapi import FastAPI

from mirumon.domain.devices.entities import Device

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
        async with device_factory(device_id=self.device_id) as device:
            url = app.url_path_for("devices:detail", device_id=device.id)
            response = await client.get(url)
            return response

    async def test_should_return_expected_response(self, response):
        assert response.status_code == self.expected_status_code
        assert response.json() == self.expected_return_payload


class TestDeviceDetail:
    @pytest.fixture(scope="class")
    def device_id(self):
        return str(uuid.uuid4())

    @pytest.fixture
    async def response(self, app: FastAPI, client, device_id, device_factory):
        async with device_factory(device_id=device_id) as device:
            url = app.url_path_for("devices:detail", device_id=device.id)
            response = await client.get(url)
            return response

    async def test_should_return_expected_response(self, response, device_id):
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


class TestDeviceSoftware:
    @pytest.fixture
    async def response(self, app: FastAPI, client, device_factory):
        async with device_factory(device_id=str(uuid.uuid4())) as device:
            url = app.url_path_for("devices:software", device_id=device.id)
            response = await client.get(url)
            return response

    async def test_should_return_expected_response(self, response):
        assert response.status_code == 200
        assert response.json() == [
            {"name": "7zip", "vendor": "7zip", "version": "1.0.0"},
            {"name": "Python3.8", "vendor": "python", "version": "3.8.0"},
        ]


class TestDeviceHardware:
    @pytest.fixture
    async def response(self, app: FastAPI, client, device_factory):
        async with device_factory(device_id=str(uuid.uuid4())) as device:
            url = app.url_path_for("devices:hardware", device_id=device.id)
            response = await client.get(url)
            return response

    async def test_should_return_expected_response(self, response):
        assert response.status_code == 200
        assert response.json() == {
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


async def test_devices_list_with_two_devices(
    app, client, devices_repo, device_factory
) -> None:
    device_id = Device.generate_id()
    device_id2 = Device.generate_id()
    device_id3 = Device.generate_id()
    system_info = {
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
    }
    properties = {"system_info": system_info}
    await devices_repo.create(Device(id=device_id, properties=properties))
    await devices_repo.create(Device(id=device_id2, properties=properties))
    await devices_repo.create(Device(id=device_id3, properties=properties))

    expected_device_1 = {
        "id": str(device_id),
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
    }
    expected_device_2 = {
        "id": str(device_id2),
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
    }
    expected_device_3 = {
        "id": str(device_id3),
        "online": False,
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
    }

    async with device_factory(device_id=device_id):
        async with device_factory(device_id=device_id2):
            url = app.url_path_for("devices:list")
            response = await client.get(url)
            items = response.json()

            assert response.status_code == 200
            assert len(items) == 3
            assert expected_device_1 in items
            assert expected_device_2 in items
            assert expected_device_3 in items


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
        assert response.status_code == 504
        assert response.json() == {"detail": "device unavailable"}
        assert response_time <= 5 + 0.5  # default for event repo + offset for test