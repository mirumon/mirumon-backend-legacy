from typing import Protocol


class Repository(Protocol):
    """Base repository class for typing and DI."""


class DeviceBrokerRepo(Repository):
    """Base broker repository class for typing and DI."""

    def __init__(self):
        pass

    async def publish_event(self, event):
        raise NotImplementedError

    async def send_command(self, command):
        raise NotImplementedError

    async def consume(self, device_id, sync_id):
        raise NotImplementedError
