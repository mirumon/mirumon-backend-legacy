from typing import Callable

from fastapi import FastAPI
from loguru import logger


def create_startup_events_handler(app: FastAPI) -> Callable:
    async def startup() -> None:
        logger.info("startup app")

    return startup


def create_shutdown_events_handler(app: FastAPI) -> Callable:
    @logger.catch
    async def shutdown() -> None:
        logger.info("shutdown app")

    return shutdown
