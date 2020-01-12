from uuid import UUID

from fastapi import FastAPI
from starlette.testclient import TestClient


def test_device_registration_success(app: FastAPI, test_client: TestClient) -> None:
    with test_client.websocket_connect(app.url_path_for("ws:service")) as websocket:
        websocket.send_json(
            {"connection_type": "registration", "shared_token": "secret"}
        )
        data = websocket.receive_json()
        assert data.get("status") == "success"
        assert UUID(data.get("device_uid"))


def test_device_registration_with_invalid_payload(
    app: FastAPI, test_client: TestClient
) -> None:
    with test_client.websocket_connect(app.url_path_for("ws:service")) as websocket:
        websocket.send_text("invalid json",)
        data = websocket.receive_json()
        assert data == {
            "message": "Expecting value: line 1 column 1 (char 0)",
            "status": "failed",
        }


def test_device_registration_without_shared_token(
    app: FastAPI, test_client: TestClient
) -> None:
    with test_client.websocket_connect(app.url_path_for("ws:service")) as websocket:
        websocket.send_json({"connection_type": "registration"},)
        data = websocket.receive_json()
        assert data == {
            "message": [
                {
                    "loc": ["shared_token"],
                    "msg": "field required",
                    "type": "value_error.missing",
                }
            ],
            "status": "failed",
        }


def test_device_registration_without_connection_type(
    app: FastAPI, test_client: TestClient
) -> None:
    with test_client.websocket_connect(app.url_path_for("ws:service")) as websocket:
        websocket.send_json({"shared_token": "secret"})
        data = websocket.receive_json()
        assert data == {
            "message": [
                {
                    "loc": ["connection_type"],
                    "msg": "field required",
                    "type": "value_error.missing",
                }
            ],
            "status": "failed",
        }


def test_device_registration_with_null_shared_token(
    app: FastAPI, test_client: TestClient
) -> None:
    with test_client.websocket_connect(app.url_path_for("ws:service")) as websocket:
        websocket.send_json({"connection_type": "registration", "shared_token": None})
        data = websocket.receive_json()
        assert data == {
            "message": [
                {
                    "loc": ["shared_token"],
                    "msg": "none is not an allowed value",
                    "type": "type_error.none.not_allowed",
                }
            ],
            "status": "failed",
        }


def test_device_registration_with_invalid_conn_type(
    app: FastAPI, test_client: TestClient
) -> None:
    with test_client.websocket_connect(app.url_path_for("ws:service")) as websocket:
        websocket.send_json(
            {"connection_type": "registrateon", "shared_token": "secret"},
        )
        data = websocket.receive_json()
        assert data == {
            "message": [
                {
                    "loc": ["connection_type"],
                    "msg": "unexpected value; permitted: <ConnectionEventType.registration: 'registration'>",
                    "type": "value_error.const",
                    "ctx": {"given": "registrateon", "permitted": ["registration"],},
                }
            ],
            "status": "failed",
        }


def test_device_registration_with_invalid_shared_token(
    app: FastAPI, test_client: TestClient
) -> None:
    with test_client.websocket_connect(app.url_path_for("ws:service")) as websocket:
        websocket.send_json(
            {"connection_type": "registration", "shared_token": "qwerty123"}
        )
        data = websocket.receive_json()
        assert data == {"message": "invalid shared token", "status": "failed"}
