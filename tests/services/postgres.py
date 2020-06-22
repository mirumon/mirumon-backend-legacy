import psycopg2
import pytest
from psycopg2._psycopg import OperationalError
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_fixed

from tests.plugins.printer import Printer

POSTGRES_DOCKER_IMAGE = "postgres:11.4-alpine"
CONTAINER_NAME = "mirumon-postgres-test"


@pytest.fixture(scope="session")
def postgres_server(create_docker_service):
    yield from create_docker_service(
        "postgres://postgres:postgres@{host}/postgres",
        POSTGRES_DOCKER_IMAGE,
        CONTAINER_NAME,
    )


@pytest.fixture(scope="session")
def postgres(postgres_server, printer):
    ping_postgres(postgres_server, printer=printer)


@retry(
    retry=(
        retry_if_exception_type(RuntimeError)
        | retry_if_exception_type(OperationalError)
    ),
    reraise=True,
    stop=stop_after_attempt(10),
    wait=wait_fixed(1),
)
def ping_postgres(dsn: str, printer: Printer):
    printer("ping postgres with dsn: {0}".format(dsn))
    conn = psycopg2.connect(dsn)
    cur = conn.cursor()
    cur.execute("SELECT now();")
    printer("postgres pong")
    cur.close()
    conn.close()
