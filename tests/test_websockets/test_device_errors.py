from threading import Thread
from time import sleep
from typing import Any

from fastapi import FastAPI
from starlette.testclient import TestClient


def test_device_decode_json_error(
    app: FastAPI, test_client: TestClient, device_ws: Any
) -> None:
    device_id = device_ws.receive_json()["device_id"]
    url = app.url_path_for("events:execute", device_id=device_id)
    response = test_client.post(url, data="decode:error")
    assert response.status_code == 400
    assert response.json() == {"detail": ["Expecting value: line 1 column 1 (char 0)"]}


def test_device_validation_error(
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


def test_device_timeout_response_error(
    app: FastAPI, test_client: TestClient, device_ws: Any
) -> None:
    device_id = device_ws.receive_json()["device_id"]
    api_url = app.url_path_for("events:details", device_id=device_id)
    response = test_client.get(api_url)
    assert response.status_code == 503
    assert response.json() == {"detail": "details event is not supported by device"}


def test_device_disconnection(
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
