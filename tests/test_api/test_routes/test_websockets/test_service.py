from uuid import UUID

from fastapi import FastAPI
from starlette.testclient import TestClient

from tests.testing_helpers import FakeClient


def test_device_registration_failed(app: FastAPI, websocket_client: TestClient) -> None:
    with websocket_client.websocket_connect(
        app.url_path_for("ws:service")
    ) as websocket:
        websocket.send_json({"connection_type": "registration", "shared_token": None})
        data = websocket.receive_json()
        assert data == {"status": "failed"}

    with websocket_client.websocket_connect(
        app.url_path_for("ws:service")
    ) as websocket:
        websocket.send_json({"connection_type": "registration"},)
        data = websocket.receive_json()
        assert data == {"status": "failed"}

    with websocket_client.websocket_connect(
        app.url_path_for("ws:service")
    ) as websocket:
        websocket.send_json({"shared_token": "secret"})
        data = websocket.receive_json()
        assert data == {"status": "failed"}

    with websocket_client.websocket_connect(
        app.url_path_for("ws:service")
    ) as websocket:
        websocket.send_json(
            {"connection_type": "registration", "shared_token": "qwerty123"}
        )
        data = websocket.receive_json()
        assert data == {"status": "failed"}

    with websocket_client.websocket_connect(
        app.url_path_for("ws:service")
    ) as websocket:
        websocket.send_json(
            {"connection_type": "registrateon", "shared_token": "secret"},
        )
        data = websocket.receive_json()
        assert data == {"status": "failed"}


def test_device_registration_success(
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


def test_empty_devices_list_rest_api(rest_client: TestClient) -> None:
    response = rest_client.get("/computers")
    assert response.status_code == 200
    assert response.json() == []


def test_devices_list_rest_api(app: FastAPI, rest_client: TestClient) -> None:
    response = rest_client.get("/computers")
    assert response.status_code == 200
    assert response.json() == []


def test_device_details_rest_api(
    rest_client: TestClient, fake_device_client: FakeClient
) -> None:
    response = rest_client.get(f"/computers/{fake_device_client.device_id}/details")
    assert (
        response.json()
        == [{"mac_address": fake_device_client.device_id, "name": "fake_device_client"}]
        and response.status_code == 200
    )
