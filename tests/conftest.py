import warnings
from inspect import Traceback
from typing import Type, Optional

import alembic.config
import pytest
from async_asgi_testclient import TestClient
from asyncpg import Connection
from asyncpg.pool import Pool
from asyncpg.transaction import Transaction
from fastapi import FastAPI

from app.main import get_app


pytest_plugins = [
    # pytest logs plugin
    "tests.plugins.printer",
    # cmd args to run docker, slow tests, etc.
    "tests.plugins.options",
    "tests.plugins.docker",
    "tests.services.postgres",
    # application
    # "tests.fixtures.application.services",
    # "tests.fixtures.application.web",
]


@pytest.fixture
def migrations(postgres):
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    alembic.config.main(argv=["upgrade", "head"])
    yield
    alembic.config.main(argv=["downgrade", "base"])


@pytest.fixture
async def app(printer) -> FastAPI:
    app = get_app()
    return app


@pytest.fixture
async def client(app: FastAPI, printer, migrations):
    async with TestClient(app, headers={"Content-Type": "application/json"}) as client:
        printer(app.state.__dict__)
        app.state.pool = await FakePool.create_pool(app.state.pool)
        connection: Connection
        async with app.state.pool.acquire() as connection:
            transaction: Transaction = connection.transaction()
            await transaction.start()
            yield client
            await transaction.rollback()
        await app.state.pool.close()


@pytest.fixture
def shared_key() -> str:
    return "shared-key-test"


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
