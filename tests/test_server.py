from starlette.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_client_websocket_connect_failed():
    with client.websocket_connect("clients/ws") as websocket:
        websocket.send_json({"mac-address": "123456789"})
        data = websocket.receive_json()
        assert data == {"status": "registration-failed"}


def test_client_websocket_connect_success():
    with client.websocket_connect("clients/ws") as websocket:
        websocket.send_json(
            {
                "mac_address": "9C-0C-25-67-10-A8",
                "name": "computer01",
                "domain": "poseidon",
                "workgroup": "workgroup",
                "current_user": {"name": "user01"},
                "os": ["Win10 Pro"],
            }
        )
        data = websocket.receive_json()
        assert data == {"status": "registration-success"}


def test_computers_list_empty():
    response = client.get("/computers")
    assert response.status_code == 200
    assert response.json() == []
