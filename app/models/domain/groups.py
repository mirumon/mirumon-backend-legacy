from uuid import UUID

from pydantic import BaseModel

from app.models.domain.users import User


class Group(BaseModel):
    id: UUID
    name: str
    owner: User
