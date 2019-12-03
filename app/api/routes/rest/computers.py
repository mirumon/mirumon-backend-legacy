from json import JSONDecodeError
from typing import Callable, List, Tuple, Type, TypeVar

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from starlette import status
from starlette.requests import Request
from starlette.websockets import WebSocketDisconnect

from app.models.schemas.computers import details, execute, hardware, shutdown, software
from app.models.schemas.events.rest import EventInRequest, RestEventType
from app.services import clients, computers, event_handlers, events

router = APIRouter()


@router.get("", response_model=List[details.ComputerInList], tags=["PC List"])
async def computers_list(
    clients_manager: computers.ClientsManager = Depends(computers.get_clients_manager),
    events_manager: events.EventsManager = Depends(events.get_events_manager),
) -> List[details.ComputerInList]:
    return await event_handlers.clients_list(clients_manager, events_manager)


def get_client(
    mac_address: str,
    clients_manager: computers.ClientsManager = Depends(computers.get_clients_manager),
) -> clients.Client:
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
                client: clients.Client = Depends(get_client),
                events_manager: events.EventsManager = Depends(
                    events.get_events_manager
                ),
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
            "/{0}/{1}".format("{mac_address}", api_event_type),
            _generate_generic_api_route(api_event_type),
            methods=[api_method],
            response_model=response_model,
            summary=f"Computer Event {api_event_type}",
            tags=["PC Events"],
        )


GET_METHOD = "GET"
POST_METHOD = "POST"

get_events = (
    (RestEventType.details, GET_METHOD, details.ComputerDetails),
    (RestEventType.hardware, GET_METHOD, hardware.HardwareModel),
    (RestEventType.hardware_mother, GET_METHOD, hardware.MotherBoardModel),
    (RestEventType.hardware_cpu, GET_METHOD, List[hardware.ProcessorModel]),
    (RestEventType.hardware_gpu, GET_METHOD, List[hardware.VideoControllerModel]),
    (RestEventType.hardware_network, GET_METHOD, List[hardware.NetworkAdapterModel]),
    (RestEventType.hardware_disks, GET_METHOD, List[hardware.PhysicalDiskModel]),
    (RestEventType.installed_programs, GET_METHOD, List[software.InstalledProgram]),
)
generate_event_routes(router, get_events)

post_events = (
    (RestEventType.shutdown, POST_METHOD, shutdown.Shutdown),
    (RestEventType.execute, POST_METHOD, execute.ExecuteResult),
)
generate_event_routes(router, post_events)
