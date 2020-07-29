import warnings
from datetime import timedelta
from inspect import Traceback
from typing import Optional, Type

import alembic.config
import pytest
from async_asgi_testclient import TestClient
from asyncpg import Connection
from asyncpg.pool import Pool
from asyncpg.transaction import Transaction
from fastapi import FastAPI

from app.main import get_app
from app.settings.components import jwt

pytest_plugins = [
    # pytest logs plugin
    "tests.plugins.printer",
    # cmd args to run docker, slow tests, etc.
    "tests.plugins.options",
    # "tests.plugins.docker",
    # "tests.services.postgres",
    # application
    # "tests.fixtures.application.services",
    # "tests.fixtures.application.web",
]


@pytest.fixture
def migrations():
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    alembic.config.main(argv=["upgrade", "head"])
    yield
    alembic.config.main(argv=["downgrade", "base"])


@pytest.fixture
def app(printer) -> FastAPI:
    app = get_app()
    return app


@pytest.fixture
async def client(app: FastAPI, token_header, printer, migrations):
    async with TestClient(
        app, headers={**token_header, "Content-Type": "application/json"}
    ) as client:
        printer(app.state.__dict__)
        app.state.db_pool = await FakePool.create_pool(app.state.db_pool)
        connection: Connection
        async with app.state.db_pool.acquire() as connection:
            transaction: Transaction = connection.transaction()
            await transaction.start()
            yield client
            await transaction.rollback()
        await app.state.db_pool.close()


@pytest.fixture
def admin(superuser_username: str, superuser_password: str):
    return {"username": superuser_username, "password": superuser_password}


@pytest.fixture
def token(admin, secret_key):
    return jwt.create_jwt_token(
        jwt_content=admin, secret_key=secret_key, expires_delta=timedelta(minutes=1),
    )


@pytest.fixture
def token_header(token):
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def secret_key() -> str:
    return "test-secret-key"


@pytest.fixture
def shared_key() -> str:
    return "test-shared-key"


@pytest.fixture
def superuser_username() -> str:
    return "test-superuser-username"


@pytest.fixture
def superuser_password() -> str:
    return "test-superuser-password"


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
