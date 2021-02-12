from fastapi import APIRouter, Depends

from mirumon.domain.users.scopes import DevicesScopes
from mirumon.infra.api.dependencies.users.permissions import check_user_scopes
from mirumon.infra.api.endpoints.devices.http import (
    auth,
    detail,
    execute,
    info,
    list,
    shutdown,
)
from mirumon.infra.api.endpoints.devices.ws import connect

router = APIRouter(tags=["Devices"])


# http
router.include_router(auth.router)
router.include_router(
    detail.router,
    dependencies=[Depends(check_user_scopes([DevicesScopes.read]))],
)
router.include_router(
    list.router,
    dependencies=[Depends(check_user_scopes([DevicesScopes.read]))],
)

router.include_router(
    info.router,
    dependencies=[Depends(check_user_scopes([DevicesScopes.read]))],
)
router.include_router(
    shutdown.router,
    dependencies=[Depends(check_user_scopes([DevicesScopes.write]))],
)
router.include_router(
    execute.router,
    dependencies=[Depends(check_user_scopes([DevicesScopes.write]))],
)

# websockets
router.include_router(connect.router)
