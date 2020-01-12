from fastapi import FastAPI
from starlette.testclient import TestClient

from tests.testing_helpers.websocket_processing_tools import process_event


def test_empty_devices_list_event(test_client: TestClient, app: FastAPI) -> None:
    url = app.url_path_for(name="events:list")
    response = test_client.get(url)
    assert response.status_code == 200
    assert response.json() == []


def test_devices_list_event(
    app: FastAPI,
    test_client: TestClient,
    client_device_factory,
    computer_inlist_payload,
) -> None:
    ws = []
    rest_resp = []
    for client in client_device_factory(3):
        payload = computer_inlist_payload.copy()
        payload["uid"] = client.uid
        payload["online"] = True
        rest_resp.append(payload)
        ws.append(client.websocket)

    event_resp_payload = {"event_result": computer_inlist_payload}
    response = process_event(
        api_method=test_client.get,
        api_kwargs=dict(url=app.url_path_for(name="events:list")),
        client_websockets=ws,
        response_payloads=[event_resp_payload, event_resp_payload, event_resp_payload],
    )
    assert response.status_code == 200
    assert response.json() == rest_resp


def test_device_details_event(
    app: FastAPI,
    test_client: TestClient,
    client_device_factory,
    computer_details_payload,
) -> None:
    for device_client in client_device_factory(1):
        api_url = app.url_path_for(name="events:details", device_uid=device_client.uid)
        response = process_event(
            api_method=test_client.get,
            api_kwargs=dict(url=api_url),
            client_websockets=[device_client.websocket],
            response_payloads=[{"event_result": computer_details_payload}],
        )

        computer_details_payload["uid"] = device_client.uid
        computer_details_payload["online"] = True

        assert response.status_code == 200
        assert response.json() == computer_details_payload
