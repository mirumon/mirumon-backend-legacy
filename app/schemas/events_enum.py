from enum import Enum


class EventTypeEnum(str, Enum):
    registration = "registration"
    auth: str = "auth"

    details = "details"

    users = "users"

    system = "system"
    hardware = "hardware"
    storage = "storage"
    network = "network"

    devices = "devices"

    installed_programs = "installed-programs"
    startup_programs = "startup-programs"
    services = "services"
    processes = "processes"

    def __str__(self):
        return self.value
