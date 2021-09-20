import asyncio
import traceback
from typing import Optional

from async_asgi_testclient.websocket import WebSocketSession

from mirumon.application.devices.internal_api_protocol.models import (
    DeviceAgentRequest,
    DeviceAgentResponse,
    StatusTypes,
)


class FakeDevice:
    def __init__(self, ws: WebSocketSession, device_id: str, loop, printer):
        self.ws = ws
        self.id = device_id
        self.loop = loop
        self.result = None
        self.printer = printer
        printer(f"init new fake device:{device_id}")

    async def receive_request(self, response_payload: Optional[dict] = None) -> dict:
        try:
            payload = await self.ws.receive_json()
        except Exception as error:  # pragma: no cover
            self.printer(f"{self} got error on receive_json:{error}")
            traceback.print_exc()

        self.printer(f"{self} received json: {repr(payload)}")
        request = DeviceAgentRequest.parse_obj(payload)

        if not response_payload:
            self.printer(f"{self} make response...")
            try:
                response_json = DeviceAgentResponse(
                    id=request.id,
                    status=StatusTypes.ok,
                    method=request.method,
                    result=self.get_event_result(request.method),
                ).json()
            except Exception as e:
                self.printer(f"{self} get error during making response: {e}")
        else:
            response_json = DeviceAgentResponse(
                id=request.id,
                status=StatusTypes.ok,
                method=request.method,
                result=response_payload,
            ).json()

        self.printer(f"{self} send payload to server {response_json}")
        await self.ws.send_text(response_json)

    def start_listen(self, response_payload: Optional[dict] = None):
        self.printer(f"{self} start listening server")
        asyncio.run_coroutine_threadsafe(
            self.receive_request(response_payload), self.loop
        )

    def get_event_result(self, method: str):
        events = {}
        events["sync_device_system"] = {
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
                },
            ],
            "last_user": {
                "name": "nick",
                "fullname": "Nick Khitrov",
                "domain": "mirumon.dev",
            },
        }
        events["sync_device_software"] = {
            "installed_programs": [
                {"name": "7zip", "vendor": "7zip", "version": "1.0.0"},
                {"name": "Python3.8", "vendor": "python", "version": "3.8.0"},
            ]
        }
        events["sync_device_hardware"] = {
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
        events["shutdown_device"] = {}
        events["execute_on_device"] = {}
        return events[method]

    def __str__(self):
        return f"FakeDevice: {self.id}"
