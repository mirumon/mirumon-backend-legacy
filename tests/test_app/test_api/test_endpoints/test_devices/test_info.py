import asyncio
import uuid
from concurrent.futures.process import ProcessPoolExecutor
from datetime import timedelta

import pytest
from async_asgi_testclient.websocket import WebSocketSession
from fastapi import FastAPI

from app.domain.device.detail import DeviceDetail
from app.domain.event.base import EventInResponse, EventInRequest
from app.settings.components.jwt import create_jwt_token

pytestmark = [pytest.mark.asyncio]


class FakeDevice:
    def __init__(self, ws: WebSocketSession, device_id, loop):
        self.ws = ws
        self.id = device_id
        self.result = None
        asyncio.run_coroutine_threadsafe(self.receive_request(), loop)

    async def receive_request(self) -> dict:
        print("start receive json from fake device")
        payload = await self.ws.receive_json()
        request = EventInRequest(**payload)

        assert self.result, "forget to call set_result()"

        response = EventInResponse(sync_id=request.sync_id, method=request.method, result=self.result)
        print("sending payload to server", response.dict())
        await self.ws.send_text(response.json())

    def set_result(self, payload: dict) -> None:
        self.result = payload


@pytest.fixture
def device_factory(app, client, secret_key, event_loop):
    async def create_device():
        device_id = uuid.uuid4()
        print(f"fake device:{device_id}")
        content = {"device_id": str(device_id)}
        token = create_jwt_token(
            jwt_content=content, secret_key=secret_key, expires_delta=timedelta(hours=1)
        )
        path = app.url_path_for("devices:service")
        async with client.websocket_connect(path=path, headers={"token": token}) as ws:
            return FakeDevice(ws, device_id, event_loop)

    return create_device

# wip
async def test_device_detail_event(app: FastAPI, client, token_header, device_factory, event_loop, secret_key):
    device_id = uuid.uuid4()
    print(f"fake device:{device_id}")
    content = {"device_id": str(device_id)}
    token = create_jwt_token(
        jwt_content=content, secret_key=secret_key, expires_delta=timedelta(hours=1)
    )
    path = app.url_path_for("devices:service")
    async with client.websocket_connect(path=path, headers={"token": token}) as ws:
        device = FakeDevice(ws, device_id, event_loop)
        payload = {
            "id": str(device.id),
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
                    "install_date": "2020-07-26T00:32:16.944988"
                },
            ],
            "last_user": {
                "name": "nick",
                "fullname": "Nick Khitrov",
                "domain": "mirumon.dev",
            },
        }
        event = DeviceDetail(online=True, **payload)
        device.set_result(payload)
        url = app.url_path_for("devices:detail", device_id=device.id)
        response = await client.get(url, headers=token_header)
        assert response.status_code == 200
        payload["online"] = True
        assert response.json() == payload


async def test_devices_list_without_registered_devices(
    app, client, token_header
) -> None:
    url = app.url_path_for("devices:list")
    response = await client.get(url, headers=token_header)
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.skip
async def test_devices_list_with_two_devices(app, client, token_header, device_factory):

    device = device_factory()
    payload = {
        "id": "8f27dd84-5547-4873-bb80-3e59e5717546",
        "online": True,
        "name": "RED-DESKTOP",
        "domain": "mirumon.dev",
        "last_user": {
            "name": "aredruss",
            "fullname": "Alexander Medyanik",
            "domain": "mirumon.dev",
        },
    }
    device.set_response(payload)

    url = app.url_path_for("devices:list")
    response = await client.get(url, headers=token_header)
    assert response.status_code == 200
    assert response.json() == [payload]


async def test_device_not_found():
    pass
