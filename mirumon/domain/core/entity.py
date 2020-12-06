from dataclasses import asdict, dataclass
from typing import Any


@dataclass(repr=True, eq=True)
class Entity:  # type: ignore
    """Base class for domain models."""

    id: Any  # type: ignore

    def dict(self) -> dict:  # type: ignore
        return asdict(self)
