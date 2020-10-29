from typing import List

from app.api.models.base import APIModel


class ExecuteCommandParams(APIModel):
    command: str
    args: List[str]
