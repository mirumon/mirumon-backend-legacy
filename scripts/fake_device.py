import asyncio
import json
from typing import Union

import websockets
from loguru import logger
from pydantic import BaseSettings
import requests

class Settings(BaseSettings):
    shared_key: str


settings = Settings()
@logger.catch
async def connect_to_server() -> None:
    try:
        token = process_registration()
        while True:
                await start_connection(token)
    except asyncio.CancelledError:
        logger.info("shutdown...")


def process_registration(
) -> str:
    logger.info("starting registration...")
    response = requests.post("localhost:8000/devices/registration", json={"shared_key": settings.shared_key})
    assert response.status_code == 201
    payload = response.json()
    return payload["device_token"]


async def start_connection(
        token: str
) -> None:
    websocket = await websockets.connect("localhost:8000/devices/")
    try:
        if not await process_registration(websocket, computer_wmi):
            exit(1)  # noqa: WPS421
    except Exception as unknown_error:
        # fixme
        #  while windows start service cant get data from wmi for unknown reason
        #  raising error for reconnecting later when wmi work
        logger.error(f"unknown error during registration {unknown_error}")
        raise RuntimeError

    while True:
        p = await websocket.recv()
        event_req = json.loads(p)
        logger.debug(f"event request: {event_req}")
        try:
            request = EventInRequest(**event_req)
        except ValidationError as request_error:
            logger.info(f"bad request: {request_error.json()}")
            continue  # todo error response when backend change events format

        try:
            event_payload: Union[PayloadInResponse, EventErrorResponse] = handle_event(
                event_type=request.event.type,
                payload=request.result,
                computer=computer_wmi,
            )
        except KeyError:
            event_payload = EventErrorResponse(error="event is not supported")
        response = EventInResponse(event=request.event, payload=event_payload).json()
        logger.bind(payload=response).debug(f"event response: {response}")
        await websocket.send(response)
    await websocket.close()


def run_service() -> None:
    loop = asyncio.get_event_loop()
    try:
        task = connect_to_server()
        asyncio.run(task)
    finally:
        loop.close()


if __name__ == "__main__":
    run_service()
