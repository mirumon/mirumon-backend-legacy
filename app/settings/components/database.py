import asyncpg
from fastapi import FastAPI
from loguru import logger

from app.settings.environments.base import AppSettings


async def create_db_connection(app: FastAPI, settings: AppSettings) -> None:
    dsn = str(settings.database_dsn)
    logger.info("Connecting to {0}", dsn)

    app.state.pool = await asyncpg.create_pool(dsn)

    logger.info("Connection established")


async def close_db_connection(app: FastAPI) -> None:
    logger.info("Closing connection to database")

    await app.state.pool.close()

    logger.info("Connection closed")
