from fastapi import FastAPI
from loguru import logger

from app.config import APP_VERSION, DEBUG
from app.endpoints.api.computers import router as computers_router
from app.endpoints.websockets import router as ws_router

app = FastAPI(title="Mirumon service", version=APP_VERSION, debug=DEBUG)

app.include_router(router=computers_router)
app.include_router(router=ws_router)


@logger.catch
async def startup() -> None:
    logger.info("startup app")


async def shutdown() -> None:
    logger.info("shutdown app")


app.add_event_handler("startup", startup)
app.add_event_handler("shutdown", shutdown)
