from fastapi import APIRouter

from app.api.endpoints import users
from app.api.endpoints.devices import auth, execute, info, ws

router = APIRouter()
router.include_router(users.router, prefix="/users", tags=["Users"])

router.include_router(auth.router, prefix="/devices", tags=["Devices Registration"])
router.include_router(info.router, prefix="/devices", tags=["Devices Information"])
router.include_router(execute.router, prefix="/devices", tags=["Devices Execute"])

router.include_router(ws.router, prefix="/devices", tags=["Devices WS"])
