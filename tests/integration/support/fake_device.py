import asyncio
import traceback
from typing import Optional

from async_asgi_testclient.websocket import WebSocketSession

from mirumon.application.devices.internal_protocol.models import (
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
        events["sync_device_system_info"] = {
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
        events["sync_device_software"] = [
            {"name": "7zip", "vendor": "7zip", "version": "1.0.0"},
            {"name": "Python3.8", "vendor": "python", "version": "3.8.0"},
        ]
        events["sync_device_hardware"] = {
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
        events["shutdown_device"] = {}
        events["execute_on_device"] = {}
        return events[method]

    def __str__(self):
        return f"FakeDevice: {self.id}"
