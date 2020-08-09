import asyncio
import json
import traceback
from datetime import datetime, timedelta
from inspect import Traceback
from typing import Optional, Type

import jwt
import pytest
from async_asgi_testclient.websocket import WebSocketSession
from asyncpg import Connection
from asyncpg.pool import Pool
from fastapi import FastAPI

from app.domain.event.base import EventInRequest, EventInResponse


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
            payload = await self.ws.receive_text()
        except Exception as error:  # pragma: no cover
            self.printer(f"{self} except error {error} during receive_json")
            traceback.print_exc()
            raise error

        request = EventInRequest.parse_raw(payload)
        if not response_payload:
            response_json = EventInResponse(
                sync_id=request.sync_id,
                method=request.method,
                result=self.get_event_result(request.method),
            ).json()
        else:
            response_json = json.dumps(response_payload)

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
        events["software"] = [
            {"name": "7zip", "vendor": "7zip", "version": "1.0.0"},
            {"name": "Python3.8", "vendor": "python", "version": "3.8.0"},
        ]
        events["hardware"] = {
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
        return events[method]

    def __str__(self):
        return f"FakeDevice: {self.id}"


class FakePoolAcquireContext:
    def __init__(self, pool: "FakePool") -> None:
        self.pool = pool

    async def __aenter__(self) -> Connection:
        return self.pool.connection

    async def __aexit__(
        self, exc_type: Type[Exception], exc_val: Exception, exc_tb: Traceback
    ) -> None:
        pass


class FakePool:
    def __init__(self, pool: Pool) -> None:
        self.pool: Pool = pool
        self.connection: Optional[Connection] = None

    @classmethod
    async def create_pool(cls, pool: Pool) -> "FakePool":
        fake = cls(pool)
        fake.connection = await pool.acquire()
        return fake

    def acquire(self) -> FakePoolAcquireContext:
        return FakePoolAcquireContext(self)

    async def close(self) -> None:
        if self.connection:  # pragma: no cover
            await self.pool.release(self.connection)
        await self.pool.close()


def create_jwt_token(
    jwt_content: dict, secret_key: str, expires_delta: timedelta,
) -> str:
    to_encode = jwt_content.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update(dict(exp=expire, sub="access"))
    return jwt.encode(to_encode, secret_key, algorithm="HS256").decode()


def decode_jwt_token(token: str, secret_key: str):
    return jwt.decode(token, secret_key, algorithms=["HS256"])
