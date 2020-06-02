import asyncpg
from fastapi import FastAPI
from loguru import logger

from app.components.config import APPSettings


async def connect_to_db(app: FastAPI, settings: APPSettings) -> None:
    dsn = str(settings.database_url)
    logger.info("Connecting to {0}", dsn)

    app.state.pool = await asyncpg.create_pool(dsn)

    logger.info("Connection established")


async def close_db_connection(app: FastAPI) -> None:
    logger.info("Closing connection to database")

    await app.state.pool.close()

    logger.info("Connection closed")
