import uuid
from threading import Thread
from time import sleep
from typing import Any

from fastapi import FastAPI
from starlette.testclient import TestClient

from tests.testing_helpers.websocket_processing_tools import process_event


def test_event_invalid_payload(
    app: FastAPI, test_client: TestClient, device_ws: Any
) -> None:
    device_ws.send_json({"invalid": "payload"})
    device_ws.receive_json()
    assert device_ws.receive_json() == {
        "error": {
            "code": 400,
            "message": [
                {
                    "loc": ["error"],
                    "msg": "must provide event_result or error",
                    "type": "value_error",
                },
                {
                    "loc": ["sync_id"],
                    "msg": "field required",
                    "type": "value_error.missing",
                },
            ],
        },
        "event_result": None,
    }


def test_event_decode_json_error(
    app: FastAPI, test_client: TestClient, device_ws: Any
) -> None:
    device_id = device_ws.receive_json()["device_id"]
    url = app.url_path_for("events:execute", device_id=device_id)
    response = test_client.post(url, data="decode:error")
    assert response.status_code == 400
    assert response.json() == {"detail": ["Expecting value: line 1 column 1 (char 0)"]}


def test_event_validation_error(
    app: FastAPI, test_client: TestClient, device_ws: Any
) -> None:
    device_id = device_ws.receive_json()["device_id"]
    url = app.url_path_for("events:execute", device_id=device_id)
    response = test_client.post(url, json={"bad": "payload"})
    assert response.status_code == 400
    assert response.json() == {
        "detail": [
            {
                "loc": ["event_params", "device_id"],
                "msg": "field required",
                "type": "value_error.missing",
            },
            {
                "loc": ["event_params", "device_id"],
                "msg": "field required",
                "type": "value_error.missing",
            },
            {
                "loc": ["event_params", "command"],
                "msg": "field required",
                "type": "value_error.missing",
            },
        ],
    }


def test_event_timeout_response_error(
    app: FastAPI, test_client: TestClient, device_ws: Any
) -> None:
    device_id = device_ws.receive_json()["device_id"]
    api_url = app.url_path_for("events:details", device_id=device_id)
    response = test_client.get(api_url)
    assert response.status_code == 503
    assert response.json() == {"detail": "details event is not supported by device"}


def test_device_disconnection_in_list_event(
    app: FastAPI, test_client: TestClient, device_ws: Any
) -> None:
    def ws_disconnect(ws: Any) -> None:
        sleep(2)
        ws.close()

    device_id = device_ws.receive_json()["device_id"]
    api_url = app.url_path_for("events:details", device_id=device_id)

    process = Thread(target=ws_disconnect, kwargs=dict(ws=device_ws),)
    process.start()

    response = test_client.get(api_url)
    process.join()

    assert response.status_code == 503
    assert response.json() == {"detail": "device disconnected"}


def test_validation_error_field_in_event(
    app: FastAPI, test_client: TestClient, device_ws: Any, details_payload
) -> None:
    device_ws.receive_json()
    device_ws.send_json({"event_result": None, "error": {"detail": "wrong event"}})
    assert device_ws.receive_json() == {
        "error": {
            "code": 400,
            "message": [
                {
                    "loc": ["error", "code"],
                    "msg": "field required",
                    "type": "value_error.missing",
                },
                {
                    "loc": ["error", "message"],
                    "msg": "field required",
                    "type": "value_error.missing",
                },
                {
                    "loc": ["sync_id"],
                    "msg": "field required",
                    "type": "value_error.missing",
                },
            ],
        },
        "event_result": None,
    }


def test_required_event_fields(
    app: FastAPI, test_client: TestClient, device_ws: Any, details_payload
) -> None:
    device_id = device_ws.receive_json()["device_id"]
    invalid_payload = dict(
        event_result=details_payload,
        error={
            "code": 1004,
            "message": "test message",
            "description": "something wrong",
        },
    )

    response = process_event(
        api_method=test_client.get,
        api_kwargs=dict(
            url=app.url_path_for(name="events:details", device_id=device_id)
        ),
        client_websockets=[device_ws],
        response_payloads=[invalid_payload],
    )

    assert response.status_code == 503
    assert response.json() == {"detail": "details event is not supported by device"}

    assert device_ws.receive_json() == {
        "error": {
            "code": 400,
            "message": [
                {
                    "loc": ["error"],
                    "msg": "must not provide both event_result and error",
                    "type": "value_error",
                }
            ],
        },
        "event_result": None,
    }


def test_validate_event_without_required_fields(
    app: FastAPI, test_client: TestClient, device_ws: Any, details_payload
) -> None:
    device_id = device_ws.receive_json()["device_id"]
    response = process_event(
        api_method=test_client.get,
        api_kwargs=dict(
            url=app.url_path_for(name="events:details", device_id=device_id)
        ),
        client_websockets=[device_ws],
        response_payloads=[{"event_result": None, "error": None}],
    )

    assert response.status_code == 503
    assert response.json() == {"detail": "details event is not supported by device"}


def test_unregistered_event(
    app: FastAPI, test_client: TestClient, device_ws: Any, details_payload
):
    device_ws.receive_json()
    device_ws.send_json({"event_result": details_payload, "sync_id": str(uuid.uuid4())})
    assert device_ws.receive_json() == {
        "error": {"code": 400, "message": "'unregistered event'"},
        "event_result": None,
    }
