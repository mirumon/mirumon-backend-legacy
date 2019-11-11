from typing import List, Tuple, Type, TypeVar, Union

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from starlette import status
from starlette.websockets import WebSocketDisconnect

from app.schemas.computers.details import ComputerDetails, ComputerInList
from app.schemas.computers.software import InstalledProgram
from app.schemas.events.rest import EventInRequest, RestEventType
from app.services.computers import ClientsManager, get_clients_manager
from app.services.event_handlers import clients_list
from app.services.events import EventsManager, get_events_manager

router = APIRouter()


@router.get("/computers", response_model=List[ComputerInList], tags=["pc"])
async def computers_list(
    clients_manager: ClientsManager = Depends(get_clients_manager),
    events_manager: EventsManager = Depends(get_events_manager),
) -> List[ComputerInList]:
    return await clients_list(clients_manager, events_manager)


APIModelT = TypeVar("APIModelT", bound=BaseModel)
EventModels = Tuple[Tuple[RestEventType, Type[APIModelT]], ...]


def generate_event_routes(api_router: APIRouter, event_models: EventModels) -> None:
    for event_type, model in event_models:
        path = "computers/{0}/{1}".format("{mac_address}", event_type)

        @api_router.get(  # noqa: WPS430
            path,
            response_model=model,
            summary=f"{event_type} Computer Event",
            tags=["PC Events"],
        )
        async def generic_api_route(
            mac_address: str,
            clients_manager: ClientsManager = Depends(get_clients_manager),
            events_manager: EventsManager = Depends(get_events_manager),
        ) -> Union[dict, list]:
            try:
                client = clients_manager.get_client(mac_address)
            except KeyError as missed_websocket_error:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="PC not found"
                ) from missed_websocket_error

            event = events_manager.generate_event(event_type)
            await client.send_event(EventInRequest(event=event))
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


events = (
    (RestEventType.details, ComputerDetails),
    (RestEventType.installed_programs, InstalledProgram),
)

generate_event_routes(router, events)
