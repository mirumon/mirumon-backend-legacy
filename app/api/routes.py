from fastapi import APIRouter, Depends

from app.api.dependencies.user_auth import check_user_scopes
from app.api.endpoints import users
from app.api.endpoints.devices import auth, info, list, ws
from app.domain.user.scopes import UserScopes

router = APIRouter()
router.include_router(users.router, prefix="/users", tags=["Users"])


DEVICES_PATH = "/devices"
router.include_router(list.router, prefix=DEVICES_PATH, tags=["Devices"])
router.include_router(auth.router, prefix=DEVICES_PATH, tags=["Devices"])
router.include_router(
    info.router,
    prefix=DEVICES_PATH,
    tags=["Devices"],
    dependencies=[Depends(check_user_scopes([UserScopes.read]))],
)

router.include_router(ws.router, prefix=DEVICES_PATH, tags=["Devices WS"])
