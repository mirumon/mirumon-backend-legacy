import logging
from json import JSONDecodeError
from typing import List, Optional

from fastapi import APIRouter, Depends, Path
from fastapi import HTTPException
from loguru import logger
from pydantic import ValidationError
from starlette.status import HTTP_404_NOT_FOUND
from starlette.websockets import WebSocket, WebSocketDisconnect

from app.manager import get_client_manager, ClientsManager
from app.schemas.computers.overview import ComputerInList
from app.schemas.computers.registration import ComputerInRegistration
from app.schemas.events import EventInRequest, Event, EventInResponse
from app.schemas.events_enum import EventTypeEnum
from app.schemas.status_enum import StatusEnum
from app.schemas.statuses import Status

router = APIRouter()


@router.get("/computers/events", response_model=List[EventTypeEnum], tags=["pc"])
def events_list() -> List[EventTypeEnum]:
    return [
        event.value
        for event in EventTypeEnum
        if event not in (EventTypeEnum.registration, EventTypeEnum.details)
    ]


@router.get("/computers", response_model=List[ComputerInList], tags=["pc"])
async def computers_list(manager: ClientsManager = Depends(get_client_manager)):
    computers = []
    for mac_address, websocket in manager.clients():
        event_id = manager.generate_event()
        event = EventInRequest(event=Event(type=EventTypeEnum.details, id=event_id))
        await websocket.send_json(event.dict())
        computer = await manager.wait_event_from_client(
            event_id=event_id, mac_address=mac_address
        )
        computers.append(computer.payload)
    return computers


@router.get(
    "/computers/{mac_address}/{event_type}", response_model=EventInResponse, tags=["pc"]
)
async def computer_details(
    mac_address: str,
    event_type: EventTypeEnum,
    manager: ClientsManager = Depends(get_client_manager),
) -> EventInResponse:
    try:
        websocket = manager.get_client(mac_address)
        event_id = manager.generate_event()

        event = EventInRequest(event=Event(type=event_type, id=event_id))
        logger.debug(event)

        await websocket.send_json(event.dict())

        payload = await manager.wait_event_from_client(
            event_id=event_id, mac_address=mac_address
        )
    except (KeyError, RuntimeError):
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="PC not found")
    return payload


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket, manager: ClientsManager = Depends(get_client_manager)
):
    await websocket.accept()
    payload = await websocket.receive_json()
    try:
        computer = ComputerInRegistration(**payload)
        manager.add_client(mac_address=computer.mac_address, websocket=websocket)

        await websocket.send_json(Status(status=StatusEnum.registration_success))
    except ValidationError:
        await websocket.send_json(Status(status=StatusEnum.registration_failed))
        await websocket.close(401)
        return

    try:
        while True:
            payload = await websocket.receive_json()
            response = EventInResponse(**payload)
            logging.debug(response)
            manager.set_event_response(
                event_id=response.event.id, payload=response.payload
            )
    except WebSocketDisconnect:
        logging.info(f"ws closed {computer.mac_address}")
    except (JSONDecodeError, ValidationError):
        logging.warning("validation error")
    finally:
        manager.remove_client(computer.mac_address)
