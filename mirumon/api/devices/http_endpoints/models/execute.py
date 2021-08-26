from typing import List

from mirumon.api.api_model import APIModel


class ExecuteCommandParams(APIModel):
    command: str
    args: List[str]
