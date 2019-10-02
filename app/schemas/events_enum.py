from enum import Enum


class EventTypeEnum(str, Enum):
    overview = "overview"
    registration = "registration"
    os = "os"
    system = "system"
    hardware = "hardware"
    storage = "storage"
    network = "network"
    devices = "devices"
    users = "users"
    installed_programs = "installed-programs"
    startup_programs = "startup-programs"
    services = "services"
    processes = "processes"

    def __str__(self):
        return self.value

