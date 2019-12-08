from fastapi import APIRouter, Depends
from loguru import logger
from pydantic import ValidationError
from starlette import websockets
from starlette.websockets import WebSocketDisconnect

from app.models.schemas.events.rest import EventInRequestWS
from app.services.clients_manager import ClientsManager, get_clients_manager
from app.services.event_handlers import (
    api_client_event_process,
    client_registration,
    process_incoming_event,
)
from app.services.events_manager import EventsManager, get_events_manager

router = APIRouter()


@router.websocket("/service", name="ws:service")
async def clients_websocket_endpoint(
    websocket: websockets.WebSocket,
    clients_manager: ClientsManager = Depends(get_clients_manager),
    events_manager: EventsManager = Depends(get_events_manager),
) -> None:
    await websocket.accept()
    try:
        # todo move to dependency
        client = await client_registration(websocket)
    except websockets.WebSocketDisconnect:
        return
    clients_manager.add_client(client)
    while True:
        try:
            logger.error("here")
            await process_incoming_event(
                clients_manager.get_client(client.device_id), events_manager
            )
        except ValidationError as error:
            logger.error(error.json())
            await websocket.send_text(error.json())
        except websockets.WebSocketDisconnect:
            logger.error("disconnected")
            await client.close()
            clients_manager.remove_client(client)
            break


@router.websocket("/clients", name="ws:clients")
async def api_websocket_endpoint(
    websocket: websockets.WebSocket,
    clients_manager: ClientsManager = Depends(get_clients_manager),
    events_manager: EventsManager = Depends(get_events_manager),
) -> None:
    await websocket.accept()
    while True:
        payload = await websocket.receive_json()
        try:
            event = EventInRequestWS(**payload)
        except ValidationError as validation_error:
            await websocket.send_text(validation_error.json())
            continue
        try:
            await api_client_event_process(
                event, websocket, clients_manager, events_manager
            )
        except KeyError:
            await websocket.send_json({"error": "device not found"})
        except WebSocketDisconnect:
            logger.info("ws api client [disconnected]")
            break
