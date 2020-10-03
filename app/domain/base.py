from pydantic import BaseModel


class Entity(BaseModel):
    """Base class for domain models."""


class ValueObject(BaseModel):
    """Base class for entities' fields."""
