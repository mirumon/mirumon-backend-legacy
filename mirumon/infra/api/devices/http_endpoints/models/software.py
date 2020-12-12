from typing import List

from mirumon.infra.api.api_model import APIModel


class InstalledProgram(APIModel):
    name: str
    vendor: str
    version: str


class ListInstalledProgram(APIModel):
    __root__: List[InstalledProgram]
