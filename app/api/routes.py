from fastapi import APIRouter, Depends

from app.api.dependencies.user_auth import check_user_scopes
from app.api.endpoints import users
from app.api.endpoints.devices import auth, info, ws
from app.domain.user.scopes import UserScopes

router = APIRouter()
router.include_router(users.router, prefix="/users", tags=["Users"])

router.include_router(auth.router, prefix="/devices", tags=["Devices"])
router.include_router(
    info.router,
    prefix="/devices",
    tags=["Devices"],
    dependencies=[Depends(check_user_scopes([UserScopes.read]))],
)

router.include_router(ws.router, prefix="/devices", tags=["Devices WS"])
