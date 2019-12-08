import time
from functools import wraps
from inspect import Traceback
from typing import Any, Callable, Optional, Type

import docker.errors
import psycopg2
from asyncpg import Connection
from asyncpg.pool import Pool
from docker import APIClient
from loguru import logger

from app.models.schemas.events.rest import DeviceID, EventInRequest, EventInResponse


def get_fake_clients_manager() -> None:
    pass


class FakeClient:
    def __init__(self, device_id: DeviceID, websocket):
        self.websocket = websocket
        logger.error(self.websocket)
        self.fake_payloads = {
            "computers-list": {
                "event_result": {
                    "mac_address": "00:d8:61:16:a5:66",
                    "name": "fake_device",
                    "username": "fake_user",
                    "domain": "fake_domain",
                    "workgroup": "fake_workgroup",
                },
            },
            "details": {
                "event_result": {
                    "mac_address": "00:d8:61:16:a5:66",
                    "name": "fake_device",
                    "domain": "fake_domain",
                    "workgroup": "fake_workgroup",
                    "user": {
                        "name": "fake_user",
                        "domain": "fake_user_domain",
                        "fullname": "fake_fullname",
                    },
                    "os": [
                        {
                            "caption": "1",
                            "version": "1",
                            "build_number": "str",
                            "os_architecture": "str",
                            "serial_number": "str",
                            "product_type": "str",
                            "number_of_users": 1,
                            "install_date": "str",
                        }
                    ],
                }
            },
        }
        self.device_id = device_id
        self.last_event = None
        self._is_connected = True
        logger.error(f"device id for fake: {device_id}")

    async def send_event(self, event: EventInRequest) -> None:
        self.last_event = event
        logger.error(event.dict())
        logger.error(f"client ws: {self.websocket}")
        await self.websocket.send_text(event.json())

    async def read_event(self) -> EventInResponse:
        logger.error("hui")
        payload = self.fake_payloads[self.last_event.method]
        r = EventInResponse(**payload, sync_id=self.last_event.sync_id)
        logger.error(r.dict())
        await self.websocket.send_text(r.json())
        return r

    @property
    def is_connected(self) -> bool:
        return self._is_connected

    async def close(self, code: int) -> None:
        self._is_connected = False


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


def do_with_retry(
    catching_exc: Type[Exception], reraised_exc: Type[Exception], error_msg: str
) -> Callable:  # pragma: no cover
    def outer_wrapper(call: Callable) -> Callable:
        @wraps(call)
        def inner_wrapper(*args: Any, **kwargs: Any) -> Any:
            delay = 0.001
            for i in range(100):
                try:
                    return call(*args, **kwargs)
                except catching_exc:
                    time.sleep(delay)
                    delay *= 2
            else:  # pragma: no cover
                raise reraised_exc(error_msg)

        return inner_wrapper

    return outer_wrapper


@do_with_retry(docker.errors.APIError, RuntimeError, "cannot pull postgres image")
def pull_image(client: APIClient, image: str) -> None:  # pragma: no cover
    client.pull(image)


@do_with_retry(psycopg2.Error, RuntimeError, "cannot start postgres server")
def ping_postgres(dsn: str) -> None:  # pragma: no cover
    conn = psycopg2.connect(dsn)
    cur = conn.cursor()
    cur.execute("CREATE EXTENSION hstore;")
    cur.close()
    conn.close()
