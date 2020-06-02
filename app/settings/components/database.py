import asyncpg
from fastapi import FastAPI
from loguru import logger

from app.settings.environments.config import DATABASE_URL


async def connect_to_db(app: FastAPI) -> None:
    logger.info("Connecting to {0}", repr(DATABASE_URL))

    app.state.pool = await asyncpg.create_pool(str(DATABASE_URL),)

    logger.info("Connection established")


async def close_db_connection(app: FastAPI) -> None:
    logger.info("Closing connection to database")

    await app.state.pool.close()

    logger.info("Connection closed")
