from typing import Protocol

# TODO: add methods and may be generic typing


class Repository(Protocol):
    """Base repository class for typing and DI."""


class BrokerRepo(Repository):
    """Base broker repository class for typing and DI."""

    def __init__(self):
        pass

    async def publish_event(self, event):
        raise NotImplementedError

    async def publish_command(self, command):
        raise NotImplementedError

    async def consume(self, sync_id):
        raise NotImplementedError
