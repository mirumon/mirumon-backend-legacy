from pydantic import BaseConfig, BaseModel


class APIModel(BaseModel):
    """
    Intended for use as a base class for externally-facing models.
    """

    class Config(BaseConfig):
        orm_mode = True
        allow_population_by_field_name = True
