from uuid import UUID

from fastapi import FastAPI
from starlette.testclient import TestClient


def test_device_registration_failed(app: FastAPI, test_client: TestClient) -> None:
    with test_client.websocket_connect(app.url_path_for("ws:service")) as websocket:
        websocket.send_json({"connection_type": "registration", "shared_token": None})
        data = websocket.receive_json()
        assert data == {"status": "failed"}

    with test_client.websocket_connect(app.url_path_for("ws:service")) as websocket:
        websocket.send_json({"connection_type": "registration"},)
        data = websocket.receive_json()
        assert data == {"status": "failed"}

    with test_client.websocket_connect(app.url_path_for("ws:service")) as websocket:
        websocket.send_json({"shared_token": "secret"})
        data = websocket.receive_json()
        assert data == {"status": "failed"}

    with test_client.websocket_connect(app.url_path_for("ws:service")) as websocket:
        websocket.send_json(
            {"connection_type": "registration", "shared_token": "qwerty123"}
        )
        data = websocket.receive_json()
        assert data == {"status": "failed"}

    with test_client.websocket_connect(app.url_path_for("ws:service")) as websocket:
        websocket.send_json(
            {"connection_type": "registrateon", "shared_token": "secret"},
        )
        data = websocket.receive_json()
        assert data == {"status": "failed"}


def test_device_registration_success(app: FastAPI, test_client: TestClient) -> None:
    with test_client.websocket_connect(app.url_path_for("ws:service")) as websocket:
        websocket.send_json(
            {"connection_type": "registration", "shared_token": "secret"}
        )
        data = websocket.receive_json()
        assert data.get("status") == "success"
        assert UUID(data.get("device_id"))


def test_empty_devices_list_rest_api(test_client: TestClient) -> None:
    response = test_client.get("/computers")
    assert response.status_code == 200
    assert response.json() == []


def test_device_details_rest_api(test_client: TestClient, app: FastAPI) -> None:
    with test_client.websocket_connect(app.url_path_for("ws:service")) as ws:
        ws.send_json({"connection_type": "registration", "shared_token": "secret"})
        device_id = ws.receive_json()["device_id"]

        response = test_client.get(
            app.url_path_for("events:details", device_id=str(device_id))
        )

        assert response.json() == {}
