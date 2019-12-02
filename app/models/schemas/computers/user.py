from pydantic import BaseModel


class User(BaseModel):
    name: str
    domain: str
    fullname: str
