import logging

from fastapi import FastAPI

from app.endpoints import router

logging.basicConfig(level=logging.DEBUG)

app = FastAPI()

app.include_router(router=router)
