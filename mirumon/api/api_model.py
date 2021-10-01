from typing import Any

from pydantic import BaseConfig, BaseModel


class APIModel(BaseModel):
    """
    Intended for use as a base class for externally-facing models.
    """

    @classmethod
    def schema(cls, by_alias: bool = True) -> Any:  # type: ignore  # noqa: WPS210
        model_schema = super().schema()
        properties = model_schema["properties"]

        for key, value in properties.items():
            if model_schema["example"][key] != ...:
                continue

            value_or_items = value.get("items") or value
            ref = value_or_items.get("$ref")
            if ref:
                model_name = ref.rsplit("#/definitions/", 1)[1]
                example = model_schema["definitions"][model_name].get("example")
                model_schema["example"][key] = example
        return model_schema

    class Config(BaseConfig):
        max_anystr_length = 256
        anystr_strip_whitespace = True
        allow_mutation = False
        use_enum_values = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
