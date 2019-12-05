from json import JSONDecodeError
from typing import Callable, List, Tuple, Type, TypeVar

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from starlette import status
from starlette.requests import Request
from starlette.websockets import WebSocketDisconnect

from app.api.dependencies.rest_api import get_client
from app.models.schemas.computers import details, execute, hardware, shutdown, software
from app.models.schemas.events.rest import EventInRequest, EventType
from app.services import clients, event_handlers
from app.services.clients_manager import ClientsManager, get_clients_manager
from app.services.events_manager import EventsManager, get_events_manager

router = APIRouter()


@router.get("", response_model=List[details.ComputerInList], tags=["Devices"])
async def computers_list(
    clients_manager: ClientsManager = Depends(get_clients_manager),
    events_manager: EventsManager = Depends(get_events_manager),
) -> List[details.ComputerInList]:
    return await event_handlers.clients_list(clients_manager, events_manager)


APIModelT = TypeVar("APIModelT", bound=BaseModel,)
EventModels = Tuple[Tuple[EventType, str, Type[APIModelT]], ...]


def generate_event_routes(api_router: APIRouter, event_models: EventModels) -> None:
    for api_event_type, api_method, response_model in event_models:

        def _generate_generic_api_route(  # noqa: WPS430
            event_type: EventType = api_event_type,
        ) -> Callable:
            async def generic_api_route(  # noqa: WPS430
                request: Request,
                client: clients.Client = Depends(get_client),
                events_manager: EventsManager = Depends(get_events_manager),
            ) -> response_model:  # type: ignore
                sync_id = events_manager.register_event()
                try:
                    payload = await request.json() if await request.body() else None
                except JSONDecodeError as decode_error:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=decode_error.args,
                    )
                await client.send_event(
                    EventInRequest(
                        method=event_type, event_params=payload, sync_id=sync_id
                    )
                )
                try:
                    return await events_manager.wait_event_from_client(
                        sync_id=sync_id, client=client
                    )
                except WebSocketDisconnect:
                    raise HTTPException(
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        detail=f"{event_type} event is not supported by device"
                        if client.is_connected
                        else "device disconnected",
                    )

            return generic_api_route

        api_router.add_api_route(
            "/{0}/{1}".format("{device_id}", api_event_type),
            _generate_generic_api_route(api_event_type),
            methods=[api_method],
            response_model=response_model,
            summary=str(api_event_type),
            tags=["Devices"],
        )


GET_METHOD = "GET"
POST_METHOD = "POST"

get_events = (
    (EventType.details, GET_METHOD, details.ComputerDetails),
    (EventType.hardware, GET_METHOD, hardware.HardwareModel),
    (EventType.hardware_mother, GET_METHOD, hardware.MotherBoardModel),
    (EventType.hardware_cpu, GET_METHOD, List[hardware.ProcessorModel]),
    (EventType.hardware_gpu, GET_METHOD, List[hardware.VideoControllerModel]),
    (EventType.hardware_network, GET_METHOD, List[hardware.NetworkAdapterModel]),
    (EventType.hardware_disks, GET_METHOD, List[hardware.PhysicalDiskModel]),
    (EventType.installed_programs, GET_METHOD, List[software.InstalledProgram]),
)
generate_event_routes(router, get_events)

post_events = (
    (EventType.shutdown, POST_METHOD, shutdown.Shutdown),
    (EventType.execute, POST_METHOD, execute.ExecuteResult),
)
generate_event_routes(router, post_events)
