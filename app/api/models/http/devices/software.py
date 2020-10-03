from app.api.models.http.base import APIModel


class InstalledProgram(APIModel):
    name: str
    vendor: str
    version: str
