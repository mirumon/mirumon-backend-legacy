import asyncpg
from loguru import logger

from mirumon.settings.environments.app import AppSettings


async def create_postgres_connection(settings: AppSettings) -> asyncpg.Pool:
    logger.info(f"Connecting to PostgreSQL with DSN `{settings.postgres_dsn}`")

    dsn = str(settings.postgres_dsn)
    postgres_pool = await asyncpg.create_pool(dsn)

    logger.info("Connection to PostgreSQL established")
    return postgres_pool


async def close_postgres_connection(postgres_pool: asyncpg.Pool) -> None:
    logger.info("Closing connection to PostgreSQL")

    await postgres_pool.close()

    logger.info("Connection to PostgreSQL closed")
