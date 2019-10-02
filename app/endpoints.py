import logging
from json import JSONDecodeError
from typing import List

from fastapi import APIRouter, Path, Depends
from fastapi import HTTPException
from loguru import logger
from pydantic import ValidationError
from starlette.status import HTTP_404_NOT_FOUND
from starlette.websockets import WebSocket, WebSocketDisconnect

from app.manager import get_client_manager, ClientsManager
from app.schemas.events import EventInRequest, Event, EventInResponse
from app.schemas.events_enum import EventTypeEnum
from app.schemas.registration import ComputerRegistration

router = APIRouter()


@router.get("/computers/events", response_model=List, tags=["pc"])
def events_list():
    return [
        event.value for event in EventTypeEnum if event != EventTypeEnum.registration
    ]


@router.get("/computers", tags=["pc"])
async def computers_list(manager: ClientsManager = Depends(get_client_manager)):
    computer_ids = []
    for computer_id, _ in manager.get_all_clients():
        computer_ids.append(computer_id)
    return computer_ids


@router.get(
    "/computers/{mac_address}/{event_type}", response_model=EventInResponse, tags=["pc"]
)
async def computer_details(
    mac_address: str,
    event_type: EventTypeEnum = Path(default=EventTypeEnum.overview),
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
    computer = ComputerRegistration(**payload)
    manager.add_client(mac_address=computer.mac_address, websocket=websocket)

    await websocket.send_json({"status": "ok"})  # todo create status enum
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
