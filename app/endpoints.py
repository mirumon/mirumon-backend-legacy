from json import JSONDecodeError
from typing import List, cast

from fastapi import APIRouter, Depends, HTTPException
from loguru import logger
from pydantic import ValidationError
from starlette import status, websockets

from app import managers, services
from app.schemas.computers.overview import ComputerInList
from app.schemas.events import Event, EventInRequest, EventInResponse
from app.schemas.events_enum import EventTypeEnum
from app.schemas.status_enum import StatusEnum
from app.schemas.statuses import Status

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
    manager: managers.ClientsManager = Depends(managers.get_client_manager)
) -> List[ComputerInList]:
    computers = []
    for mac_address, websocket in manager.clients():
        event_id = manager.generate_event()
        event = EventInRequest(event=Event(type=EventTypeEnum.details, id=event_id))
        await websocket.send_json(event.dict())
        computer = await manager.wait_event_from_client(
            event_id=event_id, mac_address=mac_address
        )
        computers.append(cast(ComputerInList, computer.payload))
    return computers


@router.get(
    "/computers/{mac_address}/{event_type}", response_model=EventInResponse, tags=["pc"]
)
async def computer_details(
    mac_address: str,
    event_type: EventTypeEnum,
    manager: managers.ClientsManager = Depends(managers.get_client_manager),
) -> EventInResponse:
    try:
        websocket = manager.get_client(mac_address)
    except KeyError as missed_websocker_error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="PC not found"
        ) from missed_websocker_error

    event_id = manager.generate_event()

    event = EventInRequest(event=Event(type=event_type, id=event_id))
    logger.debug(event)

    await websocket.send_json(event.dict())

    try:
        return await manager.wait_event_from_client(
            event_id=event_id, mac_address=mac_address
        )
    except RuntimeError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="PC disconnected"
        )


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: websockets.WebSocket,
    manager: managers.ClientsManager = Depends(managers.get_client_manager),
) -> None:
    await websocket.accept()
    try:
        computer = await services.process_registration(websocket)
    except ValidationError:
        return

    manager.add_client(mac_address=computer.mac_address, websocket=websocket)
    await websocket.send_json(Status(status=StatusEnum.registration_success))

    while True:
        try:
            await services.process_incoming_event(websocket, manager)
        except websockets.WebSocketDisconnect:
            logger.info(f"ws closed {computer.mac_address}")
        except (JSONDecodeError, ValidationError):
            logger.warning("validation error")
        finally:
            manager.remove_client(computer.mac_address)
            break
