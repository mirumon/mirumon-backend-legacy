from typing import Protocol

# TODO: add methods and may be generic typing


class Repository(Protocol):
    """Base repository class for typing and DI."""


class BrokerRepo(Protocol):
    """Base broker repository class for typing and DI."""
    def __init__(self):
        pass

    async def publish(self):
        pass

    async def consume(self, *, timeout=None):
        pass
