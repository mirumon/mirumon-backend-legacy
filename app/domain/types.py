from enum import Enum
from typing import Any, Union, NewType
from uuid import UUID
from pydantic import BaseConfig, BaseModel

from app.domain.device.execute import ExecuteCommand

DeviceUID = NewType("DeviceUID", UUID)
SyncID = NewType("SyncID", UUID)

EventParams = Union[ExecuteCommand]
Result = Any
ResultWS = Any





class APIModel(BaseModel):
    """
    Intended for use as a base class for externally-facing models.
    """

    class Config(BaseConfig):
        orm_mode = True
        allow_population_by_field_name = True
