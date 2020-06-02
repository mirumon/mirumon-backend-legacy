import uuid

import httpx
import pytest
from fastapi import FastAPI
from starlette.testclient import TestClient

from tests.testing_helpers.websocket_processing_tools import process_event


def test_empty_computers_list_event(app: FastAPI, test_client: TestClient) -> None:
    with test_client.websocket_connect(app.url_path_for("ws:clients")) as websocket:
        websocket.send_json({"method": "list"})
        data = websocket.receive_json()
        assert data == {"method": "list", "result": [], "error": None}


@pytest.mark.asyncio
async def test_computers_list_event(
    app: FastAPI, test_client: TestClient, new_clients, computer_inlist_payload,
) -> None:
    client, client2 = await new_clients(2)
    with test_client.websocket_connect(app.url_path_for("ws:clients")) as websocket:
        websocket.send_json({"method": "list"})

        sync_id = client.websocket.receive_json()["sync_id"]
        client.websocket.send_json(
            {"result": computer_inlist_payload, "sync_id": sync_id}
        )

        sync_id2 = client2.websocket.receive_json()["sync_id"]
        client2.websocket.send_json(
            {"result": computer_inlist_payload, "sync_id": sync_id2}
        )

        payload = computer_inlist_payload
        payload["online"] = True
        payload["uid"] = client.id
        payload2 = computer_inlist_payload.copy()
        payload2["uid"] = client2.id

        assert websocket.receive_json() == {
            "method": "list",
            "result": [payload, payload2],
            "error": None,
        }


def test_event_invalid_payload(device_client) -> None:
    device_client.websocket.send_json({"invalid": "payload"})
    assert device_client.websocket.receive_json() == {
        "error": {
            "code": 400,
            "message": [
                {
                    "loc": ["error"],
                    "msg": "must provide result or error",
                    "type": "value_error",
                },
                {
                    "loc": ["sync_id"],
                    "msg": "field required",
                    "type": "value_error.missing",
                },
            ],
        },
        "result": None,
    }


def test_validation_error_field_in_event(device_client) -> None:
    device_client.websocket.send_json(
        {"result": None, "error": {"detail": "wrong event"}}
    )
    assert device_client.websocket.receive_json() == {
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
        "result": None,
    }


@pytest.mark.asyncio
async def test_required_event_fields(
    app: FastAPI, client: httpx.AsyncClient, device_client, computer_details_payload
) -> None:
    invalid_payload = dict(
        result=computer_details_payload,
        error={
            "code": 1004,
            "message": "test message",
            "description": "something wrong",
        },
    )

    response = await process_event(
        api_method=client.get,
        api_kwargs=dict(
            url=app.url_path_for(name="events:detail", device_uid=device_client.id)
        ),
        client_websockets=[device_client.websocket],
        response_payloads=[invalid_payload],
    )

    assert response.status_code == 503
    assert response.json() == {"detail": "event is not supported by device"}

    assert device_client.websocket.receive_json() == {
        "error": {
            "code": 400,
            "message": [
                {
                    "loc": ["error"],
                    "msg": "must not provide both result and error",
                    "type": "value_error",
                }
            ],
        },
        "result": None,
    }


@pytest.mark.asyncio
async def test_error_response_from_device(
    app: FastAPI, client: httpx.AsyncClient, device_client
) -> None:
    invalid_payload = dict(
        error={
            "code": 1004,
            "message": "test message",
            "description": "something wrong",
        },
    )

    response = await process_event(
        api_method=client.get,
        api_kwargs=dict(
            url=app.url_path_for(name="events:detail", device_uid=device_client.id)
        ),
        client_websockets=[device_client.websocket],
        response_payloads=[invalid_payload],
    )

    assert response.status_code == 503
    assert response.json() == {"detail": {"code": 1004, "message": "test message"}}


def test_unregistered_event(
    app: FastAPI, test_client: TestClient, device_client, computer_details_payload
):
    device_client.websocket.send_json(
        {"result": computer_details_payload, "sync_id": str(uuid.uuid4())}
    )
    assert device_client.websocket.receive_json() == {
        "error": {"code": 404, "message": "'unregistered event'"},
        "result": None,
    }
