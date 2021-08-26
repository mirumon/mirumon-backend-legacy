from fastapi import APIRouter, Depends

from mirumon.api.dependencies.users.permissions import check_user_scopes
from mirumon.api.devices.http_endpoints import (
    execute_controller,
    hardware_controller,
    index_controller,
    registration_controller,
    shutdown_controller,
    software_controller,
)
from mirumon.api.devices.ws_endpoints import connect_controller
from mirumon.domain.users.scopes import DevicesScopes

router = APIRouter(tags=["Devices"])

# http
router.include_router(registration_controller.router)

router.include_router(
    index_controller.router,
    dependencies=[Depends(check_user_scopes([DevicesScopes.read]))],
)
router.include_router(
    hardware_controller.router,
    dependencies=[Depends(check_user_scopes([DevicesScopes.read]))],
)
router.include_router(
    software_controller.router,
    dependencies=[Depends(check_user_scopes([DevicesScopes.read]))],
)
router.include_router(
    shutdown_controller.router,
    dependencies=[Depends(check_user_scopes([DevicesScopes.write]))],
)
router.include_router(
    execute_controller.router,
    dependencies=[Depends(check_user_scopes([DevicesScopes.write]))],
)

# websockets
router.include_router(connect_controller.router)
