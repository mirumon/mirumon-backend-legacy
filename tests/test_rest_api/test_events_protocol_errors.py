from fastapi import FastAPI
from starlette.testclient import TestClient


def test_device_not_found(app: FastAPI, test_client: TestClient) -> None:
    api_url = app.url_path_for(
        name="events:details", device_uid="414912ac-6a9d-49bf-bb41-bc4d002e0a09"
    )
    response = test_client.get(api_url)

    assert response.status_code == 404
    assert response.json() == {"detail": "device not found"}
