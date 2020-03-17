import time
import uuid
from functools import wraps
from typing import Any, Callable, Type

import docker.errors
import psycopg2
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
