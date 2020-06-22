import os
from contextlib import ExitStack
from typing import Any

import pytest
from docker import APIClient
from docker.errors import APIError
from tenacity import retry, retry_if_exception_type, stop_after_delay, wait_fixed

from tests.plugins.printer import Printer


@pytest.fixture(scope="session")
def docker_client():
    with APIClient(version="auto") as client:
        yield client


@retry(
    retry=retry_if_exception_type(APIError),
    reraise=True,
    stop=stop_after_delay(30),
    wait=wait_fixed(2),
)
def pull_image(
    client: APIClient, image: str, printer: Printer,
) -> None:  # pragma: no cover
    printer("pulling image: {0}".format(image))
    client.pull(image)


def create_container(
    docker_client: APIClient, image: str, name: str, printer: Printer,
) -> Any:  # pragma: no cover
    pull_image(docker_client, image, printer=printer)
    ports = [5432]

    printer("creating container: {0}, {1}, {2}".format(name, ports, image))
    # try:
    #     docker_client.remove_container(container=name)
    # finally:
    return docker_client.create_container(
        image=image, name=name, ports=ports, detach=True,
    )


@pytest.fixture(scope="session")
def create_docker_service(docker_client: APIClient, printer: Printer):
    def factory(dsn_format: str, image: str, container_name: str):
        container = create_container(
            docker_client, image, container_name, printer=printer,
        )
        container_id = container["Id"]
        docker_client.start(container=container_id)
        inspection = docker_client.inspect_container(container_id)
        host = inspection["NetworkSettings"]["IPAddress"]

        with ExitStack() as stack:
            stack.callback(docker_client.remove_container, container_id)
            stack.callback(docker_client.kill, container_id)
            yield dsn_format.format(host=host)

    return factory
