from typing import Any

from fastapi import FastAPI
from starlette.testclient import TestClient


def test_empty_computers_list_event(app: FastAPI, test_client: TestClient) -> None:
    with test_client.websocket_connect(app.url_path_for("ws:clients")) as websocket:
        websocket.send_json({"method": "computers-list"})
        data = websocket.receive_json()
        assert data == {"method": "computers-list", "event_result": [], "error": None}


def test_computers_list_event(
    app: FastAPI,
    test_client: TestClient,
    device_ws: Any,
    device_ws2: Any,
    inlist_payload,
) -> None:
    device_ws.receive_json()
    device_ws2.receive_json()

    with test_client.websocket_connect(app.url_path_for("ws:clients")) as websocket:
        websocket.send_json({"method": "computers-list"})

        sync_id = device_ws.receive_json()["sync_id"]
        device_ws.send_json({"event_result": inlist_payload, "sync_id": sync_id})

        sync_id2 = device_ws2.receive_json()["sync_id"]
        device_ws2.send_json({"event_result": inlist_payload, "sync_id": sync_id2})

        assert websocket.receive_json() == {
            "method": "computers-list",
            "event_result": [inlist_payload, inlist_payload],
            "error": None,
        }
