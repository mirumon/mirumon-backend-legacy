from fastapi import APIRouter

from app.api.routes import websockets
from app.api.routes.rest import users
from app.api.routes.rest.computers import computers_list, rest_api_generator

router = APIRouter()
router.include_router(computers_list.router, prefix="/computers", tags=["Devices"])
router.include_router(rest_api_generator.router, prefix="/computers", tags=["Devices"])
router.include_router(users.router, prefix="/users", tags=["Users"])
router.include_router(websockets.router, prefix="/ws")
