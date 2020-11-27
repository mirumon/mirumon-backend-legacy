from fastapi import APIRouter, Depends

from mirumon.domain.users.scopes import UsersScopes
from mirumon.infra.api.dependencies.users.permissions import check_user_scopes
from mirumon.infra.api.endpoints.users.http import create, tokens

router = APIRouter(prefix="/users", tags=["Users"])

router.include_router(tokens.router)
router.include_router(
    create.router, dependencies=[Depends(check_user_scopes([UsersScopes.write]))]
)
