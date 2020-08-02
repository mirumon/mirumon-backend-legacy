from pydantic import BaseConfig, BaseModel
from pydantic.typing import DictStrAny


class APIModel(BaseModel):
    """
    Intended for use as a base class for externally-facing models.
    """

    @classmethod
    def schema(cls, by_alias: bool = True) -> DictStrAny:
        model_schema = super().schema()
        properties: dict = model_schema["properties"]

        for key, value in properties.items():
            # if not isinstance(, ...):
            if model_schema["example"][key] != ...:
                continue

            if "items" in value:
                value = value["items"]

            if "$ref" in value:
                model_name = value["$ref"].rsplit("#/definitions/", 1)[1]
                example = model_schema["definitions"][model_name].get("example")
                model_schema["example"][key] = example
        return model_schema

    class Config(BaseConfig):
        orm_mode = True
        allow_population_by_field_name = True
