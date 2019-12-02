from pydantic import BaseModel


class InstalledProgram(BaseModel):
    name: str
    vendor: str
    version: str
