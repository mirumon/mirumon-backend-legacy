from enum import Enum


class EventTypes(str, Enum):  # noqa: WPS600
    # system events
    error: str = "error"

    # device events
    detail: str = "detail"
    hardware: str = "hardware"
    software: str = "software"

    execute: str = "execute"
    shutdown: str = "shutdown"

    def __str__(self) -> str:
        return self.value


class StatusTypes(str, Enum):  # noqa: WPS600
    ok = "ok"
    error = "error"
