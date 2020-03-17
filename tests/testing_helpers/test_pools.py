import time
import uuid
from functools import wraps
from inspect import Traceback
from typing import Any, Callable, Optional, Type

import docker.errors
import psycopg2
from asyncpg import Connection
from asyncpg.pool import Pool
from docker import APIClient

POSTGRES_DOCKER_IMAGE = "postgres:11.4-alpine"


def do_with_retry(
    catcher_exc: Type[Exception], reraised_exc: Type[Exception], error_msg: str
) -> Callable:
    def outer_wrapper(call: Callable) -> Callable:
        @wraps(call)
        def inner_wrapper(*args: Any, **kwargs: Any) -> Any:
            delay = 0.001
            for _ in range(15):
                try:
                    return call(*args, **kwargs)
                except catcher_exc:  # pragma: no cover
                    time.sleep(delay)
                    delay *= 2
            else:
                raise reraised_exc(error_msg)  # pragma: no cover

        return inner_wrapper

    return outer_wrapper


@do_with_retry(docker.errors.APIError, RuntimeError, "cannot pull postgres image")
def pull_image(client: APIClient, image: str) -> None:
    client.pull(image)


def create_postgres_container(docker_client: APIClient) -> Any:
    pull_image(docker_client, POSTGRES_DOCKER_IMAGE)
    container = docker_client.create_container(
        image=POSTGRES_DOCKER_IMAGE,
        name="test-postgres-{}".format(uuid.uuid4()),
        ports=[5432],
        detach=True,
    )
    return container


@do_with_retry(psycopg2.OperationalError, RuntimeError, "cannot start postgres server")
def ping_postgres(dsn: str):
    conn = psycopg2.connect(dsn)
    cur = conn.cursor()
    cur.execute("CREATE EXTENSION hstore; DROP EXTENSION hstore;")
    cur.close()
    conn.close()


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
