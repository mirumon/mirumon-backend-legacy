from dataclasses import asdict, dataclass


@dataclass(repr=True, eq=True)
class DomainModel:
    """Base class for domain models."""

    def dict(self) -> dict:  # type: ignore
        return asdict(self)
