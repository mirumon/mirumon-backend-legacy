from json import JSONDecodeError

from fastapi import APIRouter, Depends
from loguru import logger
from pydantic import ValidationError
from starlette import websockets

from app.api.dependencies.services import get_devices_service, get_events_service
from app.database.repositories.events_repo import EventsService
from app.services.devices.client import DeviceClient
from app.services.devices.devices_service import DevicesService

router = APIRouter()

WS_BAD_REQUEST = 400  # fixme change to correct code
WS_UNREGISTERED_EVENT = 404
WS_NOT_FOUND = 404
SERVER_ERROR = 500


def accept_client(args):
    pass


@router.websocket("/service", name="devices:service")
async def device_ws_endpoint(
    client: DeviceClient = Depends(accept_client),
    events_service: EventsService = Depends(get_events_service),
    devices_service: DevicesService = Depends(get_devices_service),
) -> None:
    while True:
        try:
            event_response = await client.read_event()
            events_service.send_response(event_response)

        except (ValidationError, JSONDecodeError) as error:
            await client.send_error(error, WS_BAD_REQUEST)
        except KeyError as unregistered_event:
            await client.send_error(unregistered_event, WS_UNREGISTERED_EVENT)
        except websockets.WebSocketDisconnect:
            logger.error("client with uid {0} disconnected", client.device_uid)
            devices_service.disconnect_client(client)
            return
        except Exception as undefined_error:
            logger.exception("server internal error")
            await client.send_error(undefined_error, SERVER_ERROR)


@router.websocket("/clients", name="ws:clients")
async def api_websocket_endpoint(
    websocket: websockets.WebSocket,
    # clients_manager: ClientsManager = Depends(
    #     clients_manager_retriever(for_websocket=True)
    # ),
    # events_manager: EventsManager = Depends(
    #     events_manager_retriever(for_websocket=True)
    # ),
) -> None:
    await websocket.accept()
    # while True:
    # try:
    #     payload = await websocket.receive_json()
    #     event = EventInRequestWS(**payload)
    #     event_payload = await get_devices_list(clients_manager, events_manager)
    #     event_response = EventInResponseWS(
    #         method=event.method, result=event_payload
    #     )
    #     logger.debug(f"ws client response {event_response}")
    #     await websocket.send_text(event_response.json())
    # except ValidationError as validation_error:
    #     await websocket.send_text(validation_error.json())
    #     continue
    # except KeyError:  # todo add value error
    #     await websocket.send_json(
    #         EventInResponseWS(
    #             method=event.method,
    #             error=ErrorInResponse(
    #                 code=WS_NOT_FOUND, message="device not found"
    #             ),
    #         )
    #     )
    # except WebSocketDisconnect:
    #     logger.info(
    #         "{0} websocket api client {1} [closed]".format(
    #             websocket.scope.get("client", ""),
    #             websocket.scope.get("raw_path", ""),
    #         )
    #     )
    #     break
