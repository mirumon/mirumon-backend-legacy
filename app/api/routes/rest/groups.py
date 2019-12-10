from typing import List

from fastapi import APIRouter, Depends
from starlette import status

from app.api.dependencies.authentication import get_current_user
from app.api.dependencies.database import get_repository
from app.db.repositories.groups import GroupsRepository
from app.models.domain.groups import Group
from app.models.domain.users import User
from app.models.schemas.groups import GroupInCreate

router = APIRouter()


@router.get('/groups', response_model=List[Group])
async def get_user_groups(user: User = Depends(get_current_user),
                          groups_repo: GroupsRepository = Depends(
                              get_repository(GroupsRepository))) -> List[Group]:
    return await groups_repo.get_user_groups(user=user)

@router.post('/groups', status_code=status.HTTP_202_ACCEPTED, response_model=Group, )
async def create_new_group(group: GroupInCreate,
        user: User = Depends(get_current_user), group_repo: GroupsRepository = Depends(get_repository(GroupsRepository))) -> Group:
    await group_repo.create_new_group_for_user(name=group.name, devices=group.devices, user=user)