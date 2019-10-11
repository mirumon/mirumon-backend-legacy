from loguru import logger
from pydantic import ValidationError
from starlette.websockets import WebSocket

from app.managers import ClientsManager
from app.schemas.computers.registration import ComputerInRegistration
from app.schemas.events import EventInResponse
from app.schemas.status_enum import StatusEnum
from app.schemas.statuses import Status


async def process_registration(websocket: WebSocket) -> ComputerInRegistration:
    payload = await websocket.receive_json()
    try:
        return ComputerInRegistration(**payload)
    except ValidationError as wrong_schema_error:
        await websocket.send_json(Status(status=StatusEnum.registration_failed))
        await websocket.close()
        raise wrong_schema_error


async def process_incoming_event(websocket: WebSocket, manager: ClientsManager) -> None:
    payload = await websocket.receive_json()
    response = EventInResponse(**payload)
    logger.debug(response)
    manager.set_event_response(event_id=response.event.id, event=response)
