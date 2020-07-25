import aioredis
from fastapi import FastAPI
from loguru import logger

from app.settings.environments.base import AppSettings


async def create_redis_connection(app: FastAPI, settings: AppSettings) -> None:
    logger.info("Connecting to {0}", settings.redis_dsn)

    dsn = str(settings.redis_dsn)
    app.state.redis_pool = await aioredis.create_redis_pool(dsn)

    logger.info("Connection established")


async def close_redis_connection(app: FastAPI) -> None:
    logger.info("Closing connection to redis")

    redis_pool = app.state.redis_pool
    redis_pool.close()
    await redis_pool.wait_closed()

    logger.info("Connection closed")
