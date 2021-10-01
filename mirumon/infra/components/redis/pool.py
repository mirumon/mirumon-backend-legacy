import aioredis
from loguru import logger

from mirumon.settings.environments.app import AppSettings


async def create_redis_connection(settings: AppSettings) -> aioredis.Redis:
    logger.info(f"Connecting to Redis with DSN `{settings.redis_dsn}`")

    dsn = str(settings.redis_dsn)
    connection = await aioredis.create_redis_pool(dsn)

    logger.info("Connection to Redis established")
    return connection


async def close_redis_connection(connection: aioredis.Redis) -> None:
    logger.info("Closing connection to Redis")

    # gracefully closing underlying connection
    connection.close()
    await connection.wait_closed()

    logger.info("Connection to Redis closed")
