import pytest
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_fixed

import redis as redislib
from redis.exceptions import ConnectionError as RedisConnError
from tests.plugins.printer import Printer

REDIS_DOCKER_IMAGE = "redis:6.0.1-alpine"
CONTAINER_NAME = "mirumon-redis-test"


@pytest.fixture(scope="session", autouse=True)
def redis_server(use_docker, create_docker_service):
    if use_docker:  # pragma: no cover
        yield from create_docker_service(
            "redis://redis:redis@{host}/redis", REDIS_DOCKER_IMAGE, CONTAINER_NAME,
        )


@pytest.fixture
def redis(redis_server, _check_redis_connection):
    """Flush DB before tests."""
    # TODO change to aioredis and close connection
    connection = redislib.Redis.from_url(redis_server)
    connection.flushdb()
    return redis_server


def _check_redis_connection(redis_server, printer):
    ping_redis(redis_server, printer=printer)


@retry(
    retry=(
        retry_if_exception_type(RuntimeError) | retry_if_exception_type(RedisConnError)
    ),
    reraise=True,
    stop=stop_after_attempt(10),
    wait=wait_fixed(1),
)
def ping_redis(dsn: str, printer: Printer):
    printer("ping redis: {0}".format(dsn))
    connection = redislib.Redis.from_url(dsn)
    if not connection.ping():  # pragma: no cover
        raise RuntimeError("unable to receive PONG")
    printer("received PONG")
