from typing import List, Tuple, Type, TypeVar

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from starlette import status
from starlette.websockets import WebSocketDisconnect

from app.schemas.computers.details import ComputerDetails, ComputerInList
from app.schemas.events.rest import EventInRequest, EventPayload, RestEventType
from app.services.computers import ClientsManager, get_clients_manager
from app.services.event_handlers import clients_list
from app.services.events import EventsManager, get_events_manager

router = APIRouter()


@router.get("/computers/events", response_model=List[RestEventType], tags=["pc"])
def events_list() -> List[str]:
    return [event for event in RestEventType]


@router.get("/computers", response_model=List[ComputerInList], tags=["pc"])
async def computers_list(
    clients_manager: ClientsManager = Depends(get_clients_manager),
    events_manager: EventsManager = Depends(get_events_manager),
) -> List[ComputerInList]:
    return await clients_list(clients_manager, events_manager)


@router.get("/computers/{mac_address}/{event_type}", tags=["pc"])
async def computer_events(
    mac_address: str,
    event_type: RestEventType,
    clients_manager: ClientsManager = Depends(get_clients_manager),
    events_manager: EventsManager = Depends(get_events_manager),
) -> EventPayload:
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
        if client.is_connected:
            error_detail = f"{event_type} event is not supported by PC"
        else:
            error_detail = "PC disconnected"
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=error_detail
        )


####

T = TypeVar("T", bound=BaseModel)


def fill_app(values: Tuple[Tuple[str, Type[T]], ...]) -> None:
    for event_type, model in values:
        path = "computers/{mac_address}/" + event_type

        @router.get(path, response_model=model)
        async def func(
            mac_address: str,
            clients_manager: ClientsManager = Depends(get_clients_manager),
            events_manager: EventsManager = Depends(get_events_manager),
        ) -> T:
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
                if client.is_connected:
                    error_detail = f"{event_type} event is not supported by PC"
                else:
                    error_detail = "PC disconnected"
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=error_detail
                )


fill_app((("details", ComputerDetails),))
