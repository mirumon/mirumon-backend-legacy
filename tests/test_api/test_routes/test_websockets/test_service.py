from uuid import UUID

from fastapi import FastAPI
from starlette.testclient import TestClient


def test_client_websocket_connect_failed(
    app: FastAPI, websocket_client: TestClient
) -> None:
    with websocket_client.websocket_connect(
        app.url_path_for("ws:service")
    ) as websocket:
        websocket.send_json({"mac-address": "123456789"})
        data = websocket.receive_json()
        assert data == {"status": "failed"}


def test_client_websocket_connect_success(
    app: FastAPI, websocket_client: TestClient
) -> None:
    with websocket_client.websocket_connect(
        app.url_path_for("ws:service")
    ) as websocket:
        websocket.send_json(
            {"connection_type": "registration", "shared_token": "secret"}
        )
        data = websocket.receive_json()
        assert data.get("status") == "success"
        assert UUID(data.get("device_id"))
