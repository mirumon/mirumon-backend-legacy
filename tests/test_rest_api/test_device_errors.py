import uuid
from typing import Any

from fastapi import FastAPI
from starlette.testclient import TestClient


def test_device_bad_payload(
    app: FastAPI, test_client: TestClient, device_ws: Any
) -> None:
    device_ws.send_json({"bad": "payload"})
    device_ws.receive_json()
    assert device_ws.receive_json() == [
        {"loc": ["sync_id"], "msg": "field required", "type": "value_error.missing"}
    ]

    device_ws.send_json({"sync_id": str(uuid.uuid4())})
    assert device_ws.receive_json() == [{"error": "unregistered event"}]


def test_device_not_found(
    app: FastAPI, test_client: TestClient, device_ws: Any
) -> None:
    api_url = app.url_path_for(
        name="events:details", device_id="414912ac-6a9d-49bf-bb41-bc4d002e0a09"
    )
    response = test_client.get(api_url)

    assert response.status_code == 404
    assert response.json() == {"detail": "device not found"}
