from threading import Thread
from time import sleep
from typing import Any
from uuid import UUID

import pytest
from fastapi import FastAPI
from starlette.testclient import TestClient

import httpx
from tests.testing_helpers.websocket_processing_tools import (
    process_event,
    process_event_by_device,
)


@pytest.mark.asyncio
async def test_device_registration_success(
    app: FastAPI, client: httpx.AsyncClient
) -> None:
    payload = {"shared_token": "secret"}
    response = await client.post(app.url_path_for("events:registration"), json=payload)
    assert response.status_code == 202
    data = response.json()
    assert UUID(data["device_token"])


@pytest.mark.asyncio
async def test_device_registration_with_invalid_shared_token(
    app: FastAPI, client: httpx.AsyncClient
) -> None:
    payload = {"shared_token": "not-secret"}
    response = await client.post(app.url_path_for("events:registration"), json=payload)
    assert response.status_code == 401
    assert response.json() == {"detail": "invalid shared token"}


@pytest.mark.asyncio
async def test_empty_devices_list_event(
    client: httpx.AsyncClient, app: FastAPI
) -> None:
    url = app.url_path_for(name="events:list")
    response = await client.get(url)
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.slow
@pytest.mark.asyncio
async def test_devices_list_with_disconnection(
    app: FastAPI, client: httpx.AsyncClient, new_clients, computer_inlist_payload,
) -> None:
    def ws_disconnect(ws: Any) -> None:
        sleep(1)
        ws.close()

    client1, client2 = await new_clients(2)

    bad_process = Thread(target=ws_disconnect, kwargs=dict(ws=client1.websocket))

    process = Thread(
        target=process_event_by_device,
        kwargs=dict(
            client_websocket=client2.websocket,
            response_payload={"result": computer_inlist_payload},
        ),
    )
    bad_process.start()
    process.start()

    api_url = app.url_path_for("events:list")
    response = await client.get(api_url)
    bad_process.join()
    process.join()

    assert response.status_code == 200
    computer_inlist_payload["online"] = True
    computer_inlist_payload["uid"] = client2.id
    assert response.json() == [computer_inlist_payload]


@pytest.mark.slow
@pytest.mark.asyncio
async def test_devices_list_event(
    app: FastAPI, client: httpx.AsyncClient, new_clients, computer_inlist_payload,
) -> None:
    ws = []
    rest_resp = []
    for device_client in await new_clients(3):
        payload = computer_inlist_payload.copy()
        payload["uid"] = device_client.id
        payload["online"] = True
        rest_resp.append(payload)
        ws.append(device_client.websocket)

    event_resp_payload = {"result": computer_inlist_payload}
    response = await process_event(
        api_method=client.get,
        api_kwargs=dict(url=app.url_path_for(name="events:list")),
        client_websockets=ws,
        response_payloads=[event_resp_payload, event_resp_payload, event_resp_payload],
    )
    assert response.status_code == 200
    assert response.json() == rest_resp


@pytest.mark.asyncio
async def test_device_detail_event(
    app: FastAPI, client: httpx.AsyncClient, new_clients, computer_details_payload,
) -> None:
    for device_client in await new_clients(1):
        api_url = app.url_path_for(name="events:detail", device_uid=device_client.id)
        response = await process_event(
            api_method=client.get,
            api_kwargs=dict(url=api_url),
            client_websockets=[device_client.websocket],
            response_payloads=[{"result": computer_details_payload}],
        )

        computer_details_payload["uid"] = device_client.id
        computer_details_payload["online"] = True

        assert response.status_code == 200
        assert response.json() == computer_details_payload


def test_device_not_found(app: FastAPI, test_client: TestClient) -> None:
    api_url = app.url_path_for(
        name="events:detail", device_uid="414912ac-6a9d-49bf-bb41-bc4d002e0a09",
    )
    response = test_client.get(api_url)

    assert response.status_code == 404
    assert response.json() == {"detail": "device not found"}


@pytest.mark.asyncio
async def test_device_disconnection_in_detail_event(
    app: FastAPI, client: httpx.AsyncClient, device_client
) -> None:
    def ws_disconnect(ws: Any) -> None:
        sleep(2)
        ws.close()

    api_url = app.url_path_for("events:detail", device_uid=device_client.id)

    process = Thread(target=ws_disconnect, kwargs=dict(ws=device_client.websocket))
    process.start()

    response = await client.get(api_url)
    process.join()

    assert response.status_code == 503
    assert response.json() == {"detail": "device disconnected"}


@pytest.mark.asyncio
async def test_event_timeout_response_error(
    app: FastAPI, client: httpx.AsyncClient, device_client
) -> None:
    api_url = app.url_path_for("events:detail", device_uid=device_client.id)
    response = await client.get(api_url)
    assert response.status_code == 503
    assert response.json() == {"detail": "event is not supported by device"}


@pytest.mark.asyncio
async def test_event_validation_error(
    app: FastAPI, client: httpx.AsyncClient, device_client
) -> None:
    url = app.url_path_for("events:execute", device_uid=device_client.id)
    response = await client.post(url, json={"bad": "payload"})
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "loc": ["body", "command_params", "command"],
                "msg": "field required",
                "type": "value_error.missing",
            },
        ],
    }


@pytest.mark.asyncio
async def test_validate_event_without_required_fields(
    app: FastAPI, client: httpx.AsyncClient, device_client
) -> None:
    response = await process_event(
        api_method=client.get,
        api_kwargs=dict(
            url=app.url_path_for(name="events:detail", device_uid=device_client.id),
        ),
        client_websockets=[device_client.websocket],
        response_payloads=[{"result": None, "error": None}],
    )

    assert response.status_code == 503
    assert response.json() == {"detail": "event is not supported by device"}
