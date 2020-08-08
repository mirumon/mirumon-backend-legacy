import uuid
import warnings
from contextlib import asynccontextmanager
from datetime import timedelta
from typing import Optional

import alembic.config
import pytest
from async_asgi_testclient import TestClient
from asyncpg import Connection
from asyncpg.transaction import Transaction
from fastapi import FastAPI

from app.main import get_app
from tests.test_integration.support import FakeDevice, FakePool, create_jwt_token


@pytest.fixture
def device_factory(app: FastAPI, client, secret_key, event_loop, printer):
    url = app.url_path_for("devices:service")

    @asynccontextmanager
    async def create_device(
        *, device_id: Optional[str] = None, response_payload: Optional[dict] = None
    ):
        device_id = device_id or str(uuid.uuid4())
        content = {"device_id": device_id}
        token = create_jwt_token(
            jwt_content=content, secret_key=secret_key, expires_delta=timedelta(hours=1)
        )
        async with client.websocket_connect(path=url, headers={"token": token}) as ws:
            device = FakeDevice(ws, device_id, event_loop, printer)
            device.start_listen(response_payload=response_payload)
            yield device

    return create_device


@pytest.fixture
def admin(superuser_username: str, superuser_password: str):
    return {"username": superuser_username, "password": superuser_password}


@pytest.fixture
def token(admin, secret_key):
    return create_jwt_token(
        jwt_content=admin, secret_key=secret_key, expires_delta=timedelta(minutes=1),
    )


@pytest.fixture
def token_header(token):
    return {"Authorization": f"Bearer {token}"}


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
