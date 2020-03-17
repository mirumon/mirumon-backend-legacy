import warnings
from os import environ
from typing import Callable, List

import alembic
import alembic.config
import docker
import httpx
import pytest
from asgi_lifespan import LifespanManager
from asyncpg import Connection
from asyncpg.transaction import Transaction
from fastapi import FastAPI
from starlette.testclient import TestClient

from tests.testing_helpers.test_pools import ping_postgres, create_postgres_container, \
    FakePool
from tests.testing_helpers.websocket_processing_tools import DeviceClient


@pytest.fixture(scope="session")
def docker_client() -> docker.APIClient:
    with docker.APIClient(version="auto") as client:
        yield client


@pytest.fixture(scope="session", autouse=True)
def postgres_server(docker_client: docker.APIClient) -> None:
    test_db_dsn = environ.get("TEST_DB_CONNECTION")
    use_local_db = environ.get("DB")
    if test_db_dsn:  # pragma: no cover
        environ["DB_CONNECTION"] = test_db_dsn
        ping_postgres(test_db_dsn)
        yield
    elif use_local_db:  # pragma: no cover
        default_dsn = environ["DEFAULT_TEST_DB_CONNECTION"]
        environ["DB_CONNECTION"] = default_dsn
        ping_postgres(default_dsn)
        yield
    else:
        container = create_postgres_container(docker_client)
        try:
            docker_client.start(container=container["Id"])
            inspection = docker_client.inspect_container(container["Id"])
            host = inspection["NetworkSettings"]["IPAddress"]
            docker_dsn = f"postgres://postgres:postgres@{host}/postgres"
            environ["DB_CONNECTION"] = docker_dsn
            ping_postgres(docker_dsn)
            yield
        finally:
            docker_client.kill(container["Id"])
            docker_client.remove_container(container["Id"])


@pytest.fixture(autouse=True)
def migrations(postgres_server) -> None:
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    alembic.config.main(argv=["upgrade", "head"])
    yield
    alembic.config.main(argv=["downgrade", "base"])


@pytest.fixture
def app(migrations) -> FastAPI:
    from app.main import get_application  # local import for testing purpose

    return get_application()


@pytest.fixture
def test_client(app: FastAPI) -> TestClient:
    with TestClient(app) as client:
        yield client


@pytest.fixture(autouse=True)
async def client(app: FastAPI) -> httpx.AsyncClient:
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
            async with httpx.AsyncClient(
                    app=app,
                    base_url="http://testserver",
            ) as client:
                yield client
            await transaction.rollback()
        await app.state.pool.close()

        app.router.lifespan.startup_handlers = startup
        app.router.lifespan.shutdown_handlers = shutdown


@pytest.fixture
async def device_client(client: httpx.AsyncClient, test_client: TestClient,
                        app: FastAPI) -> DeviceClient:
    response = await client.post(
        app.url_path_for("events:registration"),
        json={"shared_token": environ["SHARED_TOKEN"]},
    )
    assert response.status_code == 202

    device_token = response.json()["device_token"]

    ws = test_client.websocket_connect(app.url_path_for("ws:service"))
    ws.send_json(
        {"device_token": device_token, }
    )
    uid = ws.receive_json()["device_uid"]
    yield DeviceClient(ws, uid)


@pytest.fixture
def new_clients(client: httpx.AsyncClient, app: FastAPI, test_client) -> Callable:
    async def foo(clients_count: int) -> List[DeviceClient]:
        devices = []
        for _ in range(clients_count):
            response = await client.post(
                app.url_path_for("events:registration"),
                json={"shared_token": environ["SHARED_TOKEN"]},
            )
            assert response.status_code == 202

            device_token = response.json()["device_token"]

            ws = test_client.websocket_connect(app.url_path_for("ws:service"))
            ws.send_json(
                {"device_token": device_token, }
            )
            uid = ws.receive_json()["device_uid"]
            devices.append(DeviceClient(ws, uid))
        return devices

    return foo


@pytest.fixture
def computer_inlist_payload() -> dict:
    return {
        "name": "string",
        "domain": "string",
        "workgroup": "string",
        "current_user": {"name": "string", "domain": "string", "fullname": "string"},
    }


@pytest.fixture
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
