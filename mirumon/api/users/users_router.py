from fastapi import APIRouter, Depends

from mirumon.domain.users.scopes import UsersScopes
from mirumon.api.dependencies.users.permissions import check_user_scopes
from mirumon.api.users.http_endpoints import tokens_controllers, users_controllers

router = APIRouter(tags=["Users"])

router.include_router(tokens_controllers.router)
router.include_router(
    users_controllers.router,
    dependencies=[Depends(check_user_scopes([UsersScopes.write]))],
)
