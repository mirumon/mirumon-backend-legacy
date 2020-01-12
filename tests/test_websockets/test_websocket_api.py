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
    client_device_factory,
    computer_inlist_payload,
) -> None:
    client, client2 = client_device_factory(2)
    with test_client.websocket_connect(app.url_path_for("ws:clients")) as websocket:
        websocket.send_json({"method": "computers-list"})

        sync_id = client.websocket.receive_json()["sync_id"]
        client.websocket.send_json(
            {"event_result": computer_inlist_payload, "sync_id": sync_id}
        )

        sync_id2 = client2.websocket.receive_json()["sync_id"]
        client2.websocket.send_json(
            {"event_result": computer_inlist_payload, "sync_id": sync_id2}
        )

        payload = computer_inlist_payload
        payload["online"] = True
        payload["uid"] = client.uid
        payload2 = computer_inlist_payload.copy()
        payload2["uid"] = client2.uid

        assert websocket.receive_json() == {
            "method": "computers-list",
            "event_result": [payload, payload2],
            "error": None,
        }
