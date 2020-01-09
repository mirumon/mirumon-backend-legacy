from threading import Thread
from time import sleep
from typing import Any

from fastapi import FastAPI
from starlette.testclient import TestClient

from tests.testing_helpers.websocket_processing_tools import process_event_by_device


def test_devices_list_with_disconnection(
    app: FastAPI,
    test_client: TestClient,
    device_ws: Any,
    device_ws2: Any,
    inlist_payload: Any,
) -> None:
    def ws_disconnect(ws: Any) -> None:
        sleep(1)
        ws.close()

    device_ws.receive_json()
    device_ws2.receive_json()

    api_url = app.url_path_for("events:list")

    bad_process = Thread(target=ws_disconnect, kwargs=dict(ws=device_ws),)

    process = Thread(
        target=process_event_by_device,
        kwargs=dict(
            client_websocket=device_ws2,
            response_payload={"event_result": inlist_payload},
        ),
    )
    bad_process.start()
    process.start()

    response = test_client.get(api_url)
    bad_process.join()
    process.join()

    assert response.status_code == 200
    assert response.json() == [inlist_payload]
