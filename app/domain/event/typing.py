from typing import NewType, Union
from uuid import UUID

SyncID = NewType("SyncID", UUID)
EventParams = Union[dict, list]
EventResult = Union[dict, list]
