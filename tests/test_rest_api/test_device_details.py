from typing import Any

from fastapi import FastAPI
from starlette.testclient import TestClient

from tests.testing_helpers.websocket_handlers import process_event


def test_empty_devices_list(test_client: TestClient, app: FastAPI) -> None:
    url = app.url_path_for(name="events:list")
    response = test_client.get(url)
    assert response.status_code == 200
    assert response.json() == []


def test_device_in_list(
    app: FastAPI,
    test_client: TestClient,
    device_ws: Any,
    device_ws2: Any,
    device_ws3: Any,
    inlist_payload: dict,
) -> None:
    api_url = app.url_path_for(name="events:list")
    # TODO change mac to id
    device_ids = [
        ws.receive_json()["device_id"] for ws in (device_ws, device_ws2, device_ws3)
    ]

    response = process_event(
        api_method=test_client.get,
        api_kwargs=dict(url=api_url),
        client_websockets=[device_ws, device_ws2, device_ws3],
        response_payloads=[inlist_payload, inlist_payload, inlist_payload],
    )
    assert response.status_code == 200
    assert response.json() == [inlist_payload, inlist_payload, inlist_payload]


def test_device_details(
    app: FastAPI, test_client: TestClient, device_ws: Any, details_payload: dict
) -> None:
    device_id = device_ws.receive_json()["device_id"]

    api_url = app.url_path_for(name="events:details", device_id=str(device_id))
    response = process_event(
        api_method=test_client.get,
        api_kwargs=dict(url=api_url),
        client_websockets=[device_ws],
        response_payloads=[details_payload],
    )
    assert response.status_code == 200
    assert response.json() == details_payload
