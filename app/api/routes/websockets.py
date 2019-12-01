from fastapi import APIRouter, Depends
from loguru import logger
from pydantic import ValidationError
from starlette import websockets
from starlette.websockets import WebSocketDisconnect

from app.services.computers import ClientsManager, get_clients_manager
from app.services.event_handlers import (
    client_registration,
    process_incoming_event,
    process_incoming_ws_event,
)
from app.services.events import EventsManager, get_events_manager

router = APIRouter()


@router.websocket("/service")
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
        except ValidationError as error:
            await websocket.send_text(error.json())
        except websockets.WebSocketDisconnect:
            await client.close()
            clients_manager.remove_client(client)
            break


@router.websocket("/clients")
async def api_websocket_endpoint(
    websocket: websockets.WebSocket,
    clients_manager: ClientsManager = Depends(get_clients_manager),
    events_manager: EventsManager = Depends(get_events_manager),
) -> None:
    await websocket.accept()
    while True:
        try:
            await process_incoming_ws_event(websocket, clients_manager, events_manager)
        except ValidationError as validation_error:
            await websocket.send_text(validation_error.json())
        except KeyError:
            await websocket.send_json({"error": "PC not found"})
        except WebSocketDisconnect:
            logger.debug("ws rest client [disconnected]")
            break
