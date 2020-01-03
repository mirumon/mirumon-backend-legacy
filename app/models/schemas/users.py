from typing import List, Optional

from pydantic import BaseModel

from app.models.domain.scopes import Scopes


class UserInLogin(BaseModel):
    username: str
    password: str


class UserInCreate(UserInLogin):
    scopes: List[Scopes] = []


class UserInUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    scopes: List[str] = []
