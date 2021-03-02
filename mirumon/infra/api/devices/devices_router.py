from fastapi import APIRouter, Depends

from mirumon.domain.users.scopes import DevicesScopes
from mirumon.infra.api.dependencies.users.permissions import check_user_scopes
from mirumon.infra.api.devices.http_endpoints import (
    detail_controller,
    devices_controller,
    execute_controller,
    info_controller,
    list_controller,
    shutdown_controller,
)
from mirumon.infra.api.devices.ws_endpoints import connect_controller

router = APIRouter(tags=["Devices"])


# http
router.include_router(devices_controller.router)
router.include_router(
    detail_controller.router,
    dependencies=[Depends(check_user_scopes([DevicesScopes.read]))],
)
router.include_router(
    list_controller.router,
    dependencies=[Depends(check_user_scopes([DevicesScopes.read]))],
)

router.include_router(
    info_controller.router,
    dependencies=[Depends(check_user_scopes([DevicesScopes.read]))],
)
router.include_router(
    shutdown_controller.router,
    # dependencies=[Depends(check_user_scopes([DevicesScopes.write]))],
)
router.include_router(
    execute_controller.router,
    dependencies=[Depends(check_user_scopes([DevicesScopes.write]))],
)

# websockets
router.include_router(connect_controller.router)
