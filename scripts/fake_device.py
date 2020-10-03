import asyncio
import json
import sys
from random import randint
from typing import Union

import websockets
from loguru import logger
from pydantic import BaseSettings, ValidationError
import requests

from app.api.models.ws.events.events import EventInRequest, EventInResponse


@logger.catch
async def connect_to_server(server_endpoint, token) -> None:
    while True:
        try:
            await start_connection(server_endpoint, token)
        except Exception as error:
            seconds = randint(5, 10)
            logger.error(f"got error {error}. Try to reconect after {seconds} seconds")
            await asyncio.sleep(seconds)


async def start_connection(server_endpoint: str, token: str) -> None:
    websocket = await websockets.connect(
        server_endpoint, extra_headers={"Authorization": f"Bearer {token}"}
    )
    logger.info("success connect")
    while True:
        p = await websocket.recv()
        event_req = json.loads(p)
        logger.info(f"event request: {event_req}")
        try:
            request = EventInRequest(**event_req)
        except ValidationError as request_error:
            logger.error(f"bad request: {request_error.json()}")
            continue

        try:
            event_payload = EVENT_PAYLOADS[request.method]
        except KeyError:
            logger.warning(f"event {request.method} is not supported")
            response = EventInResponse(
                status="error",
                id=request.id,
                method=request.method,
                error={"code": 503, "detail": event_payload},
            )
        else:
            response = EventInResponse(
                status="ok", id=request.id, method=request.method, result=event_payload
            )

        logger.bind(payload=response).debug(f"event response: {response.json()}")
        await websocket.send(response.json())
    await websocket.close()


EVENT_PAYLOADS = {
    "detail": {
        "name": "Manjaro-Desktop",
        "domain": "mirumon.dev",
        "workgroup": None,
        "os": [
            {
                "name": "Windows 10 Edu",
                "version": "1.12.12",
                "os_architecture": "amd64",
                "serial_number": "AGFNE-34GS-RYHRE",
                "number_of_users": 4,
            },
        ],
        "last_user": {
            "name": "nick",
            "fullname": "Nick Khitrov",
            "domain": "mirumon.dev",
        },
    },
    "software": [
        {"name": "7zip", "vendor": "7zip", "version": "1.0.0"},
        {"name": "Python3.8", "vendor": "python", "version": "3.8.0"},
    ],
    "hardware": {
        "motherboard": {
            "name": "string",
            "caption": "string",
            "status": "string",
            "product": "string",
            "serial_number": "string",
        },
        "cpu": [
            {
                "status": "string",
                "name": "string",
                "caption": "string",
                "current_clock_speed": "string",
                "current_cthread_countlock_speed": 0,
                "virtualization_firmware_enabled": True,
                "load_percentage": 0,
                "number_of_cores": 0,
                "number_of_enabled_core": 0,
                "number_of_logical_processors": 0,
            }
        ],
        "gpu": [
            {
                "status": "string",
                "name": "string",
                "caption": "string",
                "driver_version": "string",
                "driver_date": "string",
                "video_mode_description": "string",
                "current_vertical_resolution": "string",
            }
        ],
        "network": [
            {
                "description": "string",
                "mac_address": "string",
                "ip_addresses": ["string"],
            }
        ],
        "disks": [
            {
                "status": "string",
                "caption": "string",
                "serial_number": "string",
                "size": 0,
                "model": "string",
                "description": "string",
                "partitions": 0,
            }
        ],
    },
}


def register_device(server_host, shared_key: str, username: str, password: str) -> str:
    logger.info("starting user log in...")
    response = requests.post(
        f"http://{server_host}/users/token", data={"username": username, "password": password}
    )
    logger.info(response.json())
    assert response.status_code == 200
    access_token = response.json()["access_token"]

    response = requests.post(
        f"http://{server_host}/devices",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"shared_key": shared_key},
    )
    logger.info(response.json())

    assert response.status_code == 201
    payload = response.json()
    return payload["token"]


def run_service() -> None:
    loop = asyncio.get_event_loop()
    host, shared_key, username, password = sys.argv[1:5]
    device_token = register_device(host, shared_key, username, password)
    device_endpoint = f"ws://{host}/devices/service"
    try:
        task = connect_to_server(server_endpoint=device_endpoint, token=device_token)
        asyncio.run(task)
    finally:
        loop.close()


if __name__ == "__main__":
    run_service()
