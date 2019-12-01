from json import JSONDecodeError
from typing import Callable, List, Tuple, Type, TypeVar

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from starlette import status
from starlette.requests import Request
from starlette.websockets import WebSocketDisconnect

from app.schemas.computers.details import ComputerDetails, ComputerInList
from app.schemas.computers.execute import ExecuteResult
from app.schemas.computers.hardware import (
    HardwareModel,
    MotherBoardModel,
    NetworkAdapterModel,
    PhysicalDiskModel,
    ProcessorModel,
    VideoControllerModel,
)
from app.schemas.computers.shutdown import Shutdown
from app.schemas.computers.software import InstalledProgram
from app.schemas.events.rest import EventInRequest, RestEventType
from app.services.clients import Client
from app.services.computers import ClientsManager, get_clients_manager
from app.services.event_handlers import clients_list
from app.services.events import EventsManager, get_events_manager

router = APIRouter()


@router.get("/computers", response_model=List[ComputerInList], tags=["PC List"])
async def computers_list(
    clients_manager: ClientsManager = Depends(get_clients_manager),
    events_manager: EventsManager = Depends(get_events_manager),
) -> List[ComputerInList]:
    return await clients_list(clients_manager, events_manager)


def get_client(
    mac_address: str, clients_manager: ClientsManager = Depends(get_clients_manager)
) -> Client:
    try:
        return clients_manager.get_client(mac_address)
    except KeyError as missed_websocket_error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="PC not found"
        ) from missed_websocket_error


APIModelT = TypeVar("APIModelT", bound=BaseModel,)
EventModels = Tuple[Tuple[RestEventType, str, Type[APIModelT]], ...]


def generate_event_routes(api_router: APIRouter, event_models: EventModels) -> None:
    for api_event_type, api_method, response_model in event_models:

        def _generate_generic_api_route(  # noqa: WPS430
            event_type: RestEventType = api_event_type,
        ) -> Callable:
            async def generic_api_route(  # noqa: WPS430
                request: Request,
                client: Client = Depends(get_client),
                events_manager: EventsManager = Depends(get_events_manager),
            ) -> response_model:  # type: ignore
                event = events_manager.generate_event(event_type)
                try:
                    payload = await request.json() if await request.body() else None
                except JSONDecodeError as decode_error:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=decode_error.args,
                    )

                await client.send_event(EventInRequest(event=event, payload=payload))
                try:
                    return await events_manager.wait_event_from_client(
                        event_id=event.id, client=client
                    )
                except WebSocketDisconnect:
                    raise HTTPException(
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        detail=f"{event_type} event is not supported by PC"
                        if client.is_connected
                        else "PC disconnected",
                    )

            return generic_api_route

        api_router.add_api_route(
            "/computers/{0}/{1}".format("{mac_address}", api_event_type),
            _generate_generic_api_route(api_event_type),
            methods=[api_method],
            response_model=response_model,
            summary=f"Computer Event {api_event_type}",
            tags=["PC Events"],
        )


GET_METHOD = "GET"
POST_METHOD = "POST"

get_events = (
    (RestEventType.details, GET_METHOD, ComputerDetails),
    (RestEventType.hardware, GET_METHOD, HardwareModel),
    (RestEventType.hardware_mother, GET_METHOD, MotherBoardModel),
    (RestEventType.hardware_cpu, GET_METHOD, List[ProcessorModel]),
    (RestEventType.hardware_gpu, GET_METHOD, List[VideoControllerModel]),
    (RestEventType.hardware_network, GET_METHOD, List[NetworkAdapterModel]),
    (RestEventType.hardware_disks, GET_METHOD, List[PhysicalDiskModel]),
    (RestEventType.installed_programs, GET_METHOD, List[InstalledProgram]),
)
generate_event_routes(router, get_events)

post_events = (
    (RestEventType.shutdown, POST_METHOD, Shutdown),
    (RestEventType.execute, POST_METHOD, ExecuteResult),
)
generate_event_routes(router, post_events)
