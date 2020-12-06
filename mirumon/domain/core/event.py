from dataclasses import asdict, dataclass

frozen_dataclass = dataclass(repr=True, eq=True, frozen=True)


@dataclass(repr=True, eq=True)
class DomainEvent:
    """Base class for domain events."""

    def dict(self) -> dict:  # type: ignore
        return asdict(self)
