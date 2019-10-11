import logging

from fastapi import FastAPI
from loguru import logger

from app.endpoints import router

logging.basicConfig(level=logging.DEBUG)

app = FastAPI()

app.include_router(router=router)


@logger.catch
async def startup() -> None:
    logger.info("startup app")


async def shutdown() -> None:
    logger.info("shutdown app")


app.add_event_handler("startup", startup)
app.add_event_handler("shutdown", shutdown)
