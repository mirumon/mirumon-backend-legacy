from typing import Any, TypeVar

from pydantic import BaseModel

from mirumon.domain.core.entity import Entity

EntityT = TypeVar("EntityT", bound=Entity)


class InfraModel(BaseModel):  # type: ignore
    """Base class for models used in the infrastructure layer."""

    id: Any  # type: ignore

    @classmethod
    def from_entity(cls, entity: EntityT) -> BaseModel:
        return cls.parse_obj(entity.dict())

    def to_entity(self) -> EntityT:
        raise NotImplementedError
