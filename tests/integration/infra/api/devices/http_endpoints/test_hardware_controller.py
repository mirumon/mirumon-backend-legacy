import uuid

import pytest
from fastapi import FastAPI

pytestmark = [pytest.mark.asyncio]


class TestDeviceHardwareV2:
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
                "status": "ok",
                "name": "MSI b450",
                "caption": "MSI b450 Tomahawk",
                "product": "MSI",
                "serial_number": "384134g141ghwg92",
            },
            "cpu": [
                {
                    "status": "ok",
                    "name": "AMD Ryzen 5",
                    "caption": "AMD Ryzen 5",
                    "current_clock_speed": "100",
                    "current_cthread_countlock_speed": 0,
                    "virtualization_firmware_enabled": True,
                    "load_percentage": 50,
                    "number_of_cores": 12,
                    "number_of_enabled_core": 6,
                    "number_of_logical_processors": 6,
                }
            ],
            "gpu": [
                {
                    "status": "ok",
                    "name": "gtx 970",
                    "caption": "Nvidea GTX 970",
                    "driver_version": "370.9",
                    "driver_date": "12.12.12",
                    "video_mode_description": "no description",
                    "current_vertical_resolution": "1024x1024",
                }
            ],
            "network": [
                {
                    "description": "eth0",
                    "mac_address": "00:1B:44:11:3A:B7",
                    "ip_addresses": ["192.158.1.37", "192.158.1.38"],
                }
            ],
            "disks": [
                {
                    "status": "ok",
                    "caption": "Disk 1",
                    "serial_number": "123123213123",
                    "size": 10000,
                    "model": "samsung",
                    "description": "HDD",
                    "partitions": 2,
                }
            ],
        }
