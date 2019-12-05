from fastapi import APIRouter

from app.api.routes import websockets
from app.api.routes.rest import computers, users

router = APIRouter()
router.include_router(computers.router, prefix="/computers", tags=["Devices"])
router.include_router(users.router, prefix="/users", tags=["users"])
router.include_router(websockets.router, prefix="/ws")
