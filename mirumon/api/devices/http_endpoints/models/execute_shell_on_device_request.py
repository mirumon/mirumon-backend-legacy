from typing import List

from mirumon.api.api_model import APIModel


class ExecuteShellOnDeviceRequest(APIModel):
    command: str
    args: List[str]
