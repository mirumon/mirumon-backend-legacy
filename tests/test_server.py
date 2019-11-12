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
                "mac_address": "5c:f3:70:92:a1:1d",
                "name": "TEST-DESKTOP",
                "domain": "WORKGROUP",
                "current_user": {
                    "name": "testuser",
                    "domain": "TEST-DESKTOP",
                    "fullname": "test test test",
                },
                "os": [
                    {
                        "caption": "Microsoft Windows 10for Edu",
                        "version": "10.0.18362",
                        "build_number": "18362",
                        "os_architecture": "64-bit",
                        "serial_number": "00328-00090-51409-AA145",
                        "product_type": "1",
                        "number_of_users": 2,
                        "install_date": "20190707230842.000000+180",
                    }
                ],
                "workgroup": None,
            }
        )
        data = websocket.receive_json()
        assert data == {"status": "registration-success"}


def test_computers_list_empty():
    response = client.get("/computers")
    assert response.status_code == 200
    assert response.json() == []
