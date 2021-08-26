from typing import List

from mirumon.api.api_model import APIModel


class InstalledProgram(APIModel):
    name: str
    vendor: str
    version: str


class ListInstalledProgram(APIModel):
    __root__: List[InstalledProgram]
