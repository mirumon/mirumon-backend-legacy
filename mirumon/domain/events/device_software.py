from mirumon.domain.core.event import DomainEvent, frozen_dataclass


@frozen_dataclass
class InstalledProgram(DomainEvent):
    name: str
    vendor: str
    version: str
