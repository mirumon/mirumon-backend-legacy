import warnings
from os import environ

import alembic
import alembic.config
import docker
import pytest
from asyncpg import Connection
from asyncpg.transaction import Transaction
from fastapi import FastAPI
from starlette.testclient import TestClient

import httpx
from asgi_lifespan import LifespanManager
from tests.testing_helpers.test_pools import (
    FakePool,
    create_postgres_container,
    ping_postgres,
)


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
    from old_app.main import get_application  # local import for testing purpose

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
                app=app, base_url="http://testserver",
            ) as client:
                yield client
            await transaction.rollback()
        await app.state.pool.close()

        app.router.lifespan.startup_handlers = startup
        app.router.lifespan.shutdown_handlers = shutdown
