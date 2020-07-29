import asyncio
import json
import uuid
from contextlib import asynccontextmanager
from datetime import timedelta
from typing import Optional

import pytest
from async_asgi_testclient.websocket import WebSocketSession
from fastapi import FastAPI

from app.domain.event.base import EventInRequest, EventInResponse
from app.settings.components.jwt import create_jwt_token


# TODO: Add disconnect timeout to handle specific case for 503 status
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
        except Exception as error:
            self.printer(f"{self} except error {error} during receive_json")
            raise RuntimeError from error

        request = EventInRequest(**payload)

        if not response_payload:
            response_json = EventInResponse(
                sync_id=request.sync_id,
                method=request.method,
                result=self.get_event_result(request.method),
            ).json()
        else:
            response_json = json.dumps(response_payload)
        print(response_payload)

        self.printer(f"{self} send payload to server", response_json)
        await self.ws.send_text(response_json)

    def start_listen(self, response_payload: Optional[dict] = None):
        self.printer(f"{self} start listening server")
        asyncio.run_coroutine_threadsafe(
            self.receive_request(response_payload), self.loop
        )

    def get_event_result(self, method: str):
        events = {}
        events["list"] = {
            "id": self.id,
            "name": "Manjaro-Desktop",
            "domain": "mirumon.dev",
            "workgroup": None,
            "last_user": {
                "name": "nick",
                "fullname": "Nick Khitrov",
                "domain": "mirumon.dev",
            },
        }
        events["detail"] = {
            "id": self.id,
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

        return events[method]

    def __str__(self):
        return f"FakeDevice: {self.id}"


@pytest.fixture
def device_factory(app: FastAPI, client, secret_key, event_loop, printer):
    url = app.url_path_for("devices:service")

    @asynccontextmanager
    async def create_device(response_payload: Optional[dict] = None):
        device_id = str(uuid.uuid4())
        content = {"device_id": device_id}
        token = create_jwt_token(
            jwt_content=content, secret_key=secret_key, expires_delta=timedelta(hours=1)
        )
        async with client.websocket_connect(path=url, headers={"token": token}) as ws:
            device = FakeDevice(ws, device_id, event_loop, printer)
            device.start_listen(response_payload=response_payload)
            yield device

    return create_device
