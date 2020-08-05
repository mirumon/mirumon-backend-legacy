from typing import NewType
from uuid import UUID

from pydantic import SecretStr

DeviceToken = NewType("DeviceToken", str)  # for response should be str, not secret
SharedKey = NewType("SharedKey", SecretStr)
DeviceID = NewType("DeviceID", UUID)
