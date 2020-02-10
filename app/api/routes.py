from fastapi import APIRouter

from app.api.endpoints import devices, users, websockets

router = APIRouter()
router.include_router(devices.router, prefix="/devices", tags=["Devices"])
router.include_router(users.router, prefix="/users", tags=["Users"])
router.include_router(websockets.router, prefix="/ws")
