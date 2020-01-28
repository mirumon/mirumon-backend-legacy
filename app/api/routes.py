from fastapi import APIRouter

from app.api import websockets
from app.api.rest import users
from app.api.rest.computers import computers_list, device_events, rest_api_generator

router = APIRouter()
router.include_router(computers_list.router, prefix="/devices", tags=["Devices"])
router.include_router(rest_api_generator.router, prefix="/devices", tags=["Devices"])
router.include_router(device_events.router, prefix="/devices", tags=["Devices"])
router.include_router(users.router, prefix="/users", tags=["Users"])
router.include_router(websockets.router, prefix="/ws")
