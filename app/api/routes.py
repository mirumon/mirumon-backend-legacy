from fastapi import APIRouter

from app.api.endpoints import users
from app.api.endpoints.devices import rest, ws

router = APIRouter()
router.include_router(users.router, prefix="/users", tags=["Users"])

router.include_router(rest.router, prefix="/devices", tags=["Devices"])
router.include_router(ws.router, prefix="/devices", tags=["Devices WS"])
