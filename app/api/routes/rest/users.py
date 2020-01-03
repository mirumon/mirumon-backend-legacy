from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from starlette import status

from app.api.dependencies.authentication import check_user_scopes_requirements
from app.api.dependencies.database import get_repository
from app.db.repositories.users import UsersRepository
from app.models.domain.scopes import AdministrationScopes, Scopes
from app.models.schemas.users import UserInUpdate

router = APIRouter()


class UserInResponse(BaseModel):
    username: str
    scopes: List[Scopes]


@router.get(
    "",
    response_model=List[UserInResponse],
    name="users:list",
    dependencies=[Depends(check_user_scopes_requirements([AdministrationScopes.view]))],
)
async def list_all_users(
    users_repo: UsersRepository = Depends(get_repository(UsersRepository)),
    limit: int = Query(20, ge=1),
    offset: int = Query(0, ge=0),
) -> List[UserInResponse]:
    pass


@router.get(
    "/{user_id}",
    response_model=UserInResponse,
    name="users:retrieve",
    dependencies=[Depends(check_user_scopes_requirements([AdministrationScopes.view]))],
)
async def get_user_by_id(user_id: UUID) -> UserInResponse:
    pass


@router.put(
    "/{user_id}",
    response_model=UserInResponse,
    name="users:update",
    dependencies=[Depends(check_user_scopes_requirements([AdministrationScopes.edit]))],
)
async def update_user_by_id(user_id: UUID, user: UserInUpdate) -> UserInResponse:
    pass


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    name="users:delete",
    dependencies=[Depends(check_user_scopes_requirements([AdministrationScopes.edit]))],
)
async def delete_user_by_id(user_id: UUID) -> None:
    pass
