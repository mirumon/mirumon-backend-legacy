from app.database.models.base import ModelDB


class InstalledProgram(ModelDB):
    name: str
    vendor: str
    version: str
