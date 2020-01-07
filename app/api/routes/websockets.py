from fastapi import APIRouter, Depends
from loguru import logger
from pydantic import ValidationError
from starlette import websockets
from starlette.websockets import WebSocketDisconnect

from app.api.dependencies.managers import (
    clients_manager_retriever,
    events_manager_retriever,
)
from app.api.dependencies.websockets import get_accepted_websocket
from app.models.schemas.events.rest import EventInRequestWS
from app.services.clients_manager import ClientsManager
from app.services.event_handlers import (
    api_client_event_process,
    client_registration,
    process_incoming_event,
)
from app.services.events_manager import EventsManager

router = APIRouter()


@router.websocket("/service", name="ws:service")
async def clients_websocket_endpoint(
    events_manager: EventsManager = Depends(
        events_manager_retriever(for_websocket=True)
    ),
    websocket: websockets.WebSocket = Depends(get_accepted_websocket),
    manager: ClientsManager = Depends(clients_manager_retriever(for_websocket=True)),
) -> None:
    try:
        client = await client_registration(websocket)
    except ValueError:
        return

    manager.add_client(client)
    while True:
        try:
            await process_incoming_event(client, events_manager)
        except ValidationError as error:
            await client.send_error(error)
        except websockets.WebSocketDisconnect:
            logger.error("client disconnected")
            manager.remove_client(client)
            return


@router.websocket("/clients", name="ws:clients")
async def api_websocket_endpoint(
    websocket: websockets.WebSocket,
    clients_manager: ClientsManager = Depends(
        clients_manager_retriever(for_websocket=True)
    ),
    events_manager: EventsManager = Depends(
        events_manager_retriever(for_websocket=True)
    ),
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
            logger.info(
                "{0} WebSocket Api Client {1} [closed]".format(
                    websocket.scope.get("client"), websocket.scope.get("raw_path")
                )
            )
            break
