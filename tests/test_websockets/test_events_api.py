from threading import Thread
from time import sleep
from typing import Any

from fastapi import FastAPI
from starlette.testclient import TestClient

from tests.testing_helpers.websocket_processing_tools import process_event_by_device


def test_devices_list_with_disconnection(
    app: FastAPI,
    test_client: TestClient,
    client_device_factory,
    computer_inlist_payload,
) -> None:
    def ws_disconnect(ws: Any) -> None:
        sleep(1)
        ws.close()

    client, client2 = client_device_factory(2)

    bad_process = Thread(target=ws_disconnect, kwargs=dict(ws=client.websocket),)

    process = Thread(
        target=process_event_by_device,
        kwargs=dict(
            client_websocket=client2.websocket,
            response_payload={"event_result": computer_inlist_payload},
        ),
    )
    bad_process.start()
    process.start()

    api_url = app.url_path_for("events:list")
    response = test_client.get(api_url)
    bad_process.join()
    process.join()

    assert response.status_code == 200
    computer_inlist_payload["online"] = True
    computer_inlist_payload["uid"] = client2.uid
    assert response.json() == [computer_inlist_payload]
