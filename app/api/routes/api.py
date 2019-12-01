from fastapi import APIRouter

from app.api.routes import websockets
from app.api.routes.rest import computers

router = APIRouter()
router.include_router(computers.router, prefix="/computers")
router.include_router(websockets.router, prefix="/ws")
