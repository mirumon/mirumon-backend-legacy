from json import JSONDecodeError

from fastapi import APIRouter, Depends
from loguru import logger
from pydantic import ValidationError
from starlette import websockets

from app.schemas.events.base import EventErrorResponse
from app.schemas.events.ws import EventInWS
from app.services.computers import (
    ClientsManager,
    client_registration,
    clients_event_process,
    get_clients_manager,
)
from app.services.events import (
    EventsManager,
    get_events_manager,
    process_incoming_event,
)

router = APIRouter()


@router.websocket("/clients/ws")
async def clients_websocket_endpoint(
    websocket: websockets.WebSocket,
    clients_manager: ClientsManager = Depends(get_clients_manager),
    events_manager: EventsManager = Depends(get_events_manager),
) -> None:
    await websocket.accept()
    try:
        client = await client_registration(websocket)
    except websockets.WebSocketDisconnect:
        return
    clients_manager.add_client(client)
    while True:
        try:
            await process_incoming_event(client, events_manager)
        except (JSONDecodeError, ValidationError) as error:
            logger.warning("validation error")
            await websocket.send_json(EventErrorResponse(error=error.args))
        except websockets.WebSocketDisconnect:
            await client.close()
            clients_manager.remove_client(client)
            break


@router.websocket("api/ws")
async def api_websocket_endpoint(
    websocket: websockets.WebSocket,
    clients_manager: ClientsManager = Depends(get_clients_manager),
    events_manager: EventsManager = Depends(get_events_manager),
) -> None:
    await websocket.accept()
    while True:
        payload = await websocket.receive_json()
        try:
            event = EventInWS(**payload)
        except (JSONDecodeError, ValidationError) as validation_error:
            await websocket.send_json(EventErrorResponse(error=validation_error.args))
        else:
            await clients_event_process(
                event, websocket, clients_manager, events_manager
            )
