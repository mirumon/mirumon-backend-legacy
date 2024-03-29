#!/usr/bin/env python

import asyncio
import json
import sys
import uuid
from random import randint

import requests
import websockets
from loguru import logger
from pydantic import ValidationError

from mirumon.application.devices.internal_api_protocol.models import (
    DeviceAgentRequest,
    DeviceAgentResponse,
    StatusTypes,
)


@logger.catch
async def connect_to_server(server_endpoint: str, token: str) -> None:
    while True:
        try:
            await start_connection(server_endpoint, token)
        except Exception as error:
            seconds = randint(5, 10)
            logger.error(f"got error {error}. Try to reconnect after {seconds} seconds")
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
            request = DeviceAgentRequest(**event_req)
        except ValidationError as request_error:
            logger.error(f"bad request: {request_error.json()}")
            continue

        try:
            event_payload = get_event_result(request.method)
            print(f"event payload {event_payload}")
        except KeyError:
            logger.warning(f"event {request.method} is not supported")
            response = DeviceAgentResponse(
                status=StatusTypes.error,
                id=request.id,
                method=request.method,
                error={"detail": "event not supported"},
            )
        else:
            print("make response")
            response = DeviceAgentResponse(
                status=StatusTypes.ok,
                id=request.id,
                method=request.method,
                result=event_payload,
            )

        logger.debug(f"event response: {response.json()}")
        await websocket.send(response.json())


def register_device(server_host: str, username: str, password: str) -> str:
    logger.info("starting user log in...")
    response = requests.post(
        f"{server_host}/users/token",
        data={"username": username, "password": password},
    )
    logger.info(response.json())
    assert response.status_code == 200
    access_token = response.json()["access_token"]

    response = requests.post(
        f"{server_host}/devices",
        json={"name": f"Device {uuid.uuid4()}"},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    logger.info(response.json())

    assert response.status_code == 201
    payload = response.json()
    return payload["token"]


def run_service() -> None:
    loop = asyncio.get_event_loop()
    username, password = sys.argv[1:3]
    try:
        host = sys.argv[3]
    except IndexError:
        host = "http://127.0.0.1:8000"

    device_token = register_device(host, username, password)
    if host.startswith("https://"):
        _, ws_host = host.split("https://")
        device_endpoint = f"wss://{ws_host}/devices/connect/ws"
    else:
        _, ws_host = host.split("http://")
        device_endpoint = f"ws://{ws_host}/devices/connect/ws"
    try:
        task = connect_to_server(server_endpoint=device_endpoint, token=device_token)
        asyncio.run(task)
    finally:
        loop.close()


def get_event_result(method: str):
    events = {}
    events["sync_device_system_info"] = {
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
    }
    events["sync_device_software"] = {
        "installed_programs": [
            {"name": "7zip", "vendor": "7zip", "version": "1.0.0"},
            {"name": "Python3.8", "vendor": "python", "version": "3.8.0"},
        ]
    }
    events["sync_device_hardware"] = {
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
    }

    if method == "shutdown_device":
        exit(0)
    elif method == "execute_on_device":
        print("called execute_on_device...")
        return {}

    return events[method]


if __name__ == "__main__":
    run_service()
