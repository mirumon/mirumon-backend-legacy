from typing import Dict, List, Union, cast

from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from app.schemas.computers.overview import ComputerInList
from app.schemas.events import EventInResponse, EventTypeEnum
from app.services.computers import ClientsManager, get_clients_manager
from app.services.events import EventsManager, get_events_manager

router = APIRouter()


@router.get("/computers/events", response_model=List[EventTypeEnum], tags=["pc"])
def events_list() -> List[str]:
    return [
        event
        for event in EventTypeEnum
        if event not in {EventTypeEnum.registration, EventTypeEnum.details}
    ]


@router.get("/computers", response_model=List[ComputerInList], tags=["pc"])
async def computers_list(
    clients_manager: ClientsManager = Depends(get_clients_manager),
    events_manager: EventsManager = Depends(get_events_manager),
) -> List[ComputerInList]:
    computers = []
    for client in clients_manager.clients():
        event = events_manager.generate_event(EventTypeEnum.details)
        await client.send_event(event)
        computer = await events_manager.wait_event_from_client(
            event_id=event.id, client=client
        )
        computers.append(cast(ComputerInList, computer))
    return cast(List, computers)


@router.get(
    "/computers/{mac_address}/{event_type}", response_model=EventInResponse, tags=["pc"]
)
async def computer_details(
    mac_address: str,
    event_type: EventTypeEnum,
    clients_manager: ClientsManager = Depends(get_clients_manager),
    events_manager: EventsManager = Depends(get_events_manager),
) -> Union[List, Dict]:
    try:
        client = clients_manager.get_client(mac_address)
    except KeyError as missed_websocket_error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="PC not found"
        ) from missed_websocket_error

    event = events_manager.generate_event(event_type)
    await client.send_event(event)
    try:
        return await events_manager.wait_event_from_client(
            event_id=event.id, client=client
        )
    except RuntimeError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="PC disconnected"
        )
