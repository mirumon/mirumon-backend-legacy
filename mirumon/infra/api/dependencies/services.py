from types import MappingProxyType
from typing import Callable, Type, Union

from mirumon.application.devices.auth_service import DevicesAuthService
from mirumon.application.devices.devices_service import DevicesService
from mirumon.application.events.events_service import EventsService
from mirumon.application.users.auth_service import AuthUsersService
from mirumon.infra.api.dependencies.devices.devices_services import (
    get_devices_auth_service,
    get_devices_service,
    get_events_service,
)
from mirumon.infra.api.dependencies.users.users_services import get_auth_users_service

ServiceTypes = Type[
    Union[AuthUsersService, EventsService, DevicesService, DevicesAuthService]
]


def get_service(  # type: ignore
    service_type: ServiceTypes,
) -> Callable[..., object]:
    for registered_service_type, factory in SERVICE_FACTORIES.items():
        if issubclass(service_type, registered_service_type):
            return factory
    raise ValueError(f"{service_type} not found in registered repos")


SERVICE_FACTORIES = MappingProxyType(
    {
        AuthUsersService: get_auth_users_service,
        EventsService: get_events_service,
        DevicesService: get_devices_service,
        DevicesAuthService: get_devices_auth_service,
    }
)
