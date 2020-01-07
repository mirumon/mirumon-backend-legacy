import uuid
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


def test_device_not_found(
    app: FastAPI, test_client: TestClient, device_ws: Any, details_payload: dict
) -> None:
    api_url = app.url_path_for(
        name="events:details", device_id="414912ac-6a9d-49bf-bb41-bc4d002e0a09"
    )
    response = test_client.get(api_url)

    assert response.status_code == 404
    assert response.json() == {"detail": "device not found"}


def test_device_bad_payload(
    app: FastAPI, test_client: TestClient, device_ws: Any, details_payload: dict
) -> None:
    device_ws.send_json({"bad": "payload"})
    device_ws.receive_json()
    response_payload = device_ws.receive_json()
    assert response_payload == [
        {"loc": ["sync_id"], "msg": "field required", "type": "value_error.missing"}
    ]

    device_ws.send_json({"sync_id": str(uuid.uuid4())})
    response_payload = device_ws.receive_json()
    assert response_payload == [{"error": "unregistered event"}]
