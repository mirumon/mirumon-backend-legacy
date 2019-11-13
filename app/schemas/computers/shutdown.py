from pydantic import BaseModel


class Shutdown(BaseModel):
    shutdown: str
