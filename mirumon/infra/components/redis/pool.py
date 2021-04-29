import aioredis
from fastapi import FastAPI
from loguru import logger

from mirumon.settings.environments.app import AppSettings


async def create_redis_connection(app: FastAPI, settings: AppSettings) -> None:
    logger.info("Connecting to {0}", settings.redis_dsn)

    dsn = str(settings.redis_dsn)
    connection = await aioredis.create_redis_pool(dsn)

    # add to app state to use in controllers over DI
    app.state.redis_conn = connection
    logger.info("Redis connection established")


async def close_redis_connection(app: FastAPI) -> None:
    logger.info("Closing connection to redis")

    connection = app.state.redis_conn

    # gracefully closing underlying connection
    connection.close()
    await connection.wait_closed()

    logger.info("Redis connection closed")
