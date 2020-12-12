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
from passlib.context import CryptContext

from mirumon.domain.users.entities import User
from mirumon.domain.users.scopes import DevicesScopes, UsersScopes
from mirumon.infra.api.asgi import create_app
from mirumon.infra.users.users_repo_impl import UsersRepositoryImplementation
from mirumon.settings.config import get_app_settings
from mirumon.settings.environments.app import AppSettings
from tests.integration.support.fake_device import FakeDevice
from tests.integration.support.fake_pool import FakePool
from tests.integration.support.jwt import create_jwt_token


@pytest.fixture
def default_settings() -> AppSettings:
    return get_app_settings()


@pytest.fixture
async def app(default_settings, migrations) -> FastAPI:
    app = create_app(default_settings)
    return app


@pytest.fixture
def migrations():
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    alembic.config.main(argv=["upgrade", "head"])
    yield
    alembic.config.main(argv=["downgrade", "base"])


@pytest.fixture
async def client(app: FastAPI, token_header, superuser_username, superuser_password):
    """Superuser client for testing only logic. Create another client fixture
    in module or package to test permissions."""
    async with TestClient(
        app, headers={**token_header, "Content-Type": "application/json"}
    ) as client:
        # Change db pools in client because
        # TestClient trigger server events for connections init
        app.state.postgres_pool = await FakePool.create_pool(app.state.postgres_pool)
        connection: Connection
        async with app.state.postgres_pool.acquire() as connection:
            transaction: Transaction = connection.transaction()
            await transaction.start()
            repo = UsersRepositoryImplementation(connection)
            salt = "fakesalt"
            hashed_password = CryptContext(schemes=["bcrypt"], deprecated="auto").hash(
                salt + superuser_password
            )
            user_id = User.generate_id()
            new_user = User(
                id=user_id,
                username=superuser_username,
                salt=salt,
                hashed_password=hashed_password,
                scopes=[
                    DevicesScopes.write,
                    DevicesScopes.read,
                    UsersScopes.read,
                    UsersScopes.write,
                ],
            )
            await repo.create(new_user)
            yield client
            await transaction.rollback()
        await app.state.postgres_pool.close()


@pytest.fixture
def token_header(token):
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def token(superuser_username: str, secret_key):
    admin = {"username": superuser_username, "scopes": [DevicesScopes.read]}
    return create_jwt_token(
        jwt_content=admin,
        secret_key=secret_key,
        expires_delta=timedelta(minutes=10),
    )


@pytest.fixture
def device_factory(app: FastAPI, client, secret_key, event_loop, printer):
    @asynccontextmanager
    async def create_device(
        *, device_id: Optional[str] = None, response_payload: Optional[dict] = None
    ):
        url = app.url_path_for("devices:service")
        device_id = device_id or str(uuid.uuid4())
        content = {"device": {"id": device_id}}
        token = create_jwt_token(
            jwt_content=content, secret_key=secret_key, expires_delta=timedelta(hours=1)
        )
        async with client.websocket_connect(
            path=url, headers={"Authorization": f"Bearer {token}"}
        ) as ws:
            device = FakeDevice(ws, device_id, event_loop, printer)
            device.start_listen(response_payload=response_payload)
            yield device

    return create_device
