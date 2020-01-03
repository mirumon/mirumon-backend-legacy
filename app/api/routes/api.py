from fastapi import APIRouter

from app.api.routes import websockets
from app.api.routes.rest import auth, computers, users

router = APIRouter()
router.include_router(computers.router, prefix="/computers")
router.include_router(auth.router, prefix="/users", tags=["users"])
router.include_router(websockets.router, prefix="/ws")
router.include_router(users.router, prefix="/users", tags=["users"])
