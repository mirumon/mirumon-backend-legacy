from typing import List

from mirumon.infra.api.api_model import APIModel


class ExecuteCommandParams(APIModel):
    command: str
    args: List[str]
