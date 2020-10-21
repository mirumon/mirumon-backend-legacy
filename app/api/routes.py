from fastapi import APIRouter, Depends

from app.api.dependencies.users.permissions import check_user_scopes
from app.api.endpoints.http import users
from app.api.endpoints.http.devices import auth, detail, info, list, shutdown
from app.api.endpoints.ws.devices import ws
from app.domain.user.scopes import DevicesScopes

router = APIRouter()

DEVICES_PATH = "/devices"
DEVICES_TAG = "Devices"

USERS_PATH = "/users"
USERS_TAG = "Users"

# Users routers
router.include_router(users.router, prefix=USERS_PATH, tags=[USERS_TAG])

# Devices routers
router.include_router(
    auth.router,
    prefix=DEVICES_PATH,
    tags=[DEVICES_TAG],
)
router.include_router(
    list.router,
    prefix=DEVICES_PATH,
    tags=[DEVICES_TAG],
    dependencies=[Depends(check_user_scopes([DevicesScopes.read]))],
)
router.include_router(
    detail.router,
    prefix=DEVICES_PATH,
    tags=[DEVICES_TAG],
    dependencies=[Depends(check_user_scopes([DevicesScopes.read]))],
)
router.include_router(
    shutdown.router,
    prefix=DEVICES_PATH,
    tags=[DEVICES_TAG],
    dependencies=[Depends(check_user_scopes([DevicesScopes.write]))],
)
router.include_router(
    info.router,
    prefix=DEVICES_PATH,
    tags=[DEVICES_TAG],
    dependencies=[Depends(check_user_scopes([DevicesScopes.read]))],
)

router.include_router(ws.router, prefix=DEVICES_PATH, tags=[DEVICES_TAG])
