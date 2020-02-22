import uuid
import warnings
from collections import namedtuple
from os import environ, getenv
from typing import Callable, List, Optional

import alembic
import docker as libdocker
import pytest
from asgi_lifespan import LifespanManager
from asyncpg import Connection
from asyncpg.transaction import Transaction
from fastapi import FastAPI
from httpx import Client
from starlette.testclient import TestClient

from tests.testing_helpers.test_pools import FakePool, ping_postgres, pull_image

POSTGRES_DOCKER_IMAGE = "postgres:11.4-alpine"

environ["SECRET_KEY"] = "secret"
environ["SHARED_TOKEN"] = "secret"
environ["REST_MAX_RESPONSE_TIME"] = "2.0"
environ["REST_SLEEP_TIME"] = "0.5"

USE_LOCAL_DB = getenv("USE_LOCAL_DB_FOR_TEST", False)


@pytest.fixture
def app() -> FastAPI:
    from app.main import get_application  # local import for testing purpose

    return get_application()


@pytest.fixture
def test_client(app: FastAPI) -> None:
    with TestClient(app) as client:
        yield client


DeviceClient = namedtuple("DeviceClient", ["websocket", "uid"])


@pytest.fixture
def device_client(test_client: TestClient, app: FastAPI) -> DeviceClient:
    response = test_client.post(
        app.url_path_for("events:registration"),
        json={"shared_token": environ["SHARED_TOKEN"]},
    )
    assert response.status_code == 202

    device_token = response.json()["device_token"]

    ws = test_client.websocket_connect(app.url_path_for("ws:service"))
    ws.send_json(
        {"device_token": device_token,}
    )
    uid = ws.receive_json()["device_uid"]
    yield DeviceClient(ws, uid)


@pytest.fixture
def client_device_factory(
    test_client: TestClient, app: FastAPI
) -> Callable[[int], List[DeviceClient]]:
    def device_client(clients_count: int) -> List[DeviceClient]:
        for _ in range(clients_count):
            response = test_client.post(
                app.url_path_for("events:registration"),
                json={"shared_token": environ["SHARED_TOKEN"]},
            )
            assert response.status_code == 202

            device_token = response.json()["device_token"]

            ws = test_client.websocket_connect(app.url_path_for("ws:service"))
            ws.send_json(
                {"device_token": device_token,}
            )
            uid = ws.receive_json()["device_uid"]
            yield DeviceClient(ws, uid)

    return device_client


@pytest.fixture(scope="session")
def docker() -> Optional[libdocker.APIClient]:
    if USE_LOCAL_DB:  # pragma: no cover
        return None
    return libdocker.APIClient(version="auto")  # pragma: no cover


@pytest.fixture(scope="session", autouse=True)
def postgres_server(docker: libdocker.APIClient) -> None:
    warnings.filterwarnings("ignore", category=DeprecationWarning)

    if not USE_LOCAL_DB:  # pragma: no cover
        pull_image(docker, POSTGRES_DOCKER_IMAGE)

        container = docker.create_container(
            image=POSTGRES_DOCKER_IMAGE,
            name="test-postgres-{}".format(uuid.uuid4()),
            detach=True,
        )
        docker.start(container=container["Id"])
        inspection = docker.inspect_container(container["Id"])
        host = inspection["NetworkSettings"]["IPAddress"]

        dsn = f"postgres://postgres:postgres@{host}/postgres"

        try:
            ping_postgres(dsn)
            environ["DB_CONNECTION"] = dsn

            alembic.config.main(argv=["upgrade", "head"])

            yield container

            alembic.config.main(argv=["downgrade", "base"])
        finally:
            docker.kill(container["Id"])
            docker.remove_container(container["Id"])
    else:  # pragma: no cover
        yield
        return


# here starts db transaction that is required for almost all tests
@pytest.fixture(autouse=True)
async def client(app: FastAPI) -> Client:
    async with LifespanManager(app):
        startup = app.router.lifespan.startup_handlers
        shutdown = app.router.lifespan.shutdown_handlers

        app.router.lifespan.startup_handlers = []
        app.router.lifespan.shutdown_handlers = []

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

        app.router.lifespan.startup_handlers = startup
        app.router.lifespan.shutdown_handlers = shutdown


@pytest.fixture(scope="session")
def computer_inlist_payload() -> dict:
    return {
        "name": "string",
        "domain": "string",
        "workgroup": "string",
        "current_user": {"name": "string", "domain": "string", "fullname": "string"},
    }


@pytest.fixture(scope="session")
def computer_details_payload() -> dict:
    return {
        "name": "string",
        "domain": "string",
        "workgroup": "string",
        "current_user": {"name": "string", "domain": "string", "fullname": "string"},
        "os": [
            {
                "name": "string",
                "version": "string",
                "os_architecture": "string",
                "serial_number": "string",
                "number_of_users": 1,
                "install_date": "2020-01-12T06:29:25.774088",
            }
        ],
    }
