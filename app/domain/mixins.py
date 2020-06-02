import datetime
from uuid import UUID

from pydantic import BaseModel, validator


class IDModelMixin(BaseModel):
    id: UUID = None  # type: ignore
