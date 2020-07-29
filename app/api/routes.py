from fastapi import APIRouter, Depends

from app.api.dependencies.user_auth import check_user_scopes
from app.api.endpoints import users
from app.api.endpoints.devices import auth, execute, info, ws
from app.domain.user.scopes import UserScopes
from app.settings.components.logger import logger

router = APIRouter()
router.include_router(users.router, prefix="/users", tags=["Users"])

router.include_router(auth.router, prefix="/devices", tags=["Devices Registration"])
router.include_router(
    info.router,
    prefix="/devices",
    tags=["Devices Information"],
    dependencies=[Depends(check_user_scopes([UserScopes.read]))],
)
router.include_router(
    execute.router,
    prefix="/devices",
    tags=["Devices Execute"],
    dependencies=[Depends(check_user_scopes([UserScopes.execute]))],
)

router.include_router(ws.router, prefix="/devices", tags=["Devices WS"])

for r in router.routes:
    logger.debug(r.name)
