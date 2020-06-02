from fastapi import APIRouter

from app.api.endpoints import users
from app.api.endpoints.devices import info, ws

router = APIRouter()
router.include_router(users.router, prefix="/users", tags=["Users"])

router.include_router(info.router, prefix="/devices", tags=["Devices"])
router.include_router(ws.router, prefix="/devices", tags=["Devices WS"])
