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

    with test_client.websocket_connect(app.url_path_for("ws:service")) as websocket:
        websocket.send_text(
            "bad json",
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
