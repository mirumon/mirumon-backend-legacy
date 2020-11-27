import asyncpg
from fastapi import FastAPI
from loguru import logger

from mirumon.settings.environments.base import AppSettings


async def create_postgres_connection(app: FastAPI, settings: AppSettings) -> None:
    logger.info("Connecting to {0}", settings.postgres_dsn)

    dsn = str(settings.postgres_dsn)
    app.state.postgres_pool = await asyncpg.create_pool(dsn)  # type: ignore

    logger.info("Connection established")


async def close_postgres_connection(app: FastAPI) -> None:
    logger.info("Closing connection to infra")

    await app.state.postgres_pool.close()  # type: ignore

    logger.info("Connection closed")
