from os import environ, getenv
from uuid import UUID

import pytest
from asgi_lifespan import LifespanManager
from asyncpg import Connection
from asyncpg.transaction import Transaction
from fastapi import FastAPI
from httpx import Client
from loguru import logger
from starlette.testclient import TestClient

from app.services.clients_manager import get_clients_manager
from tests.testing_helpers import FakeClient, FakePool, get_fake_clients_manager

POSTGRES_DOCKER_IMAGE = "postgres:11.4-alpine"

environ["SECRET_KEY"] = "secret"
environ["SHARED_TOKEN"] = "secret"

USE_LOCAL_DB = getenv("USE_LOCAL_DB_FOR_TEST", True)


#
# @pytest.fixture(scope="session")
# def docker() -> libdocker.APIClient:
#     return libdocker.APIClient(version="auto")
#
#
# @pytest.fixture(scope="session", autouse=True)
# def postgres_server(docker: libdocker.APIClient) -> None:
#     warnings.filterwarnings("ignore", category=DeprecationWarning)
#
#     if not USE_LOCAL_DB:  # pragma: no cover
#         pull_image(docker, POSTGRES_DOCKER_IMAGE)
#
#         container = docker.create_container(
#             image=POSTGRES_DOCKER_IMAGE,
#             name="test-postgres-{}".format(uuid.uuid4()),
#             detach=True,
#         )
#         docker.start(container=container["Id"])
#         inspection = docker.inspect_container(container["Id"])
#         host = inspection["NetworkSettings"]["IPAddress"]
#
#         dsn = f"postgres://postgres:postgres@{host}/postgres"
#
#         try:
#             ping_postgres(dsn)
#             environ["DB_CONNECTION"] = dsn
#
#             alembic.config.main(argv=["upgrade", "head"])
#
#             yield container
#
#             alembic.config.main(argv=["downgrade", "base"])
#         finally:
#             docker.kill(container["Id"])
#             docker.remove_container(container["Id"])
#     else:  # pragma: no cover
#         yield
#         return

# here starts db transaction that is required for almost all tests
@pytest.fixture(autouse=True)
async def client(app: FastAPI) -> Client:
    async with LifespanManager(app):
        app.state.pool = await FakePool.create_pool(app.state.pool)
        connection: Connection
        async with app.state.pool.acquire() as connection:
            transaction: Transaction = connection.transaction()
            await transaction.start()
            async with Client(
                app=app,
                base_url="http://testserver",
                headers={"Content-Type": "application/json"},
            ) as client:
                yield client
            await transaction.rollback()
        await app.state.pool.close()


@pytest.fixture
def app() -> FastAPI:
    from app.main import get_application  # local import for testing purpose

    return get_application()


@pytest.fixture
def fake_app() -> FastAPI:
    from app.main import get_application  # local import for testing purpose

    app = get_application()
    app.dependency_overrides[get_clients_manager] = get_fake_clients_manager
    return app


@pytest.fixture
def websocket_client(app: FastAPI) -> None:
    with TestClient(app) as client:
        yield client


@pytest.fixture
def rest_client(app: FastAPI) -> None:
    with TestClient(app) as client:
        yield client


@pytest.fixture
def fake_device_client(app: FastAPI, websocket_client: TestClient) -> None:
    websocket = websocket_client.websocket_connect(app.url_path_for("ws:service"))
    websocket.send_json({"connection_type": "registration", "shared_token": "secret"})
    data = websocket.receive_json()
    manager = get_clients_manager()
    device_id = UUID(data["device_id"])
    client = manager.get_client(device_id)
    manager.remove_client(client)
    logger.error(f"first client ws: {client.websocket}")
    fake_client = FakeClient(device_id=device_id, websocket=client.websocket)
    manager.add_client(fake_client)
    assert fake_client.websocket == manager.clients[0].websocket
    yield fake_client
