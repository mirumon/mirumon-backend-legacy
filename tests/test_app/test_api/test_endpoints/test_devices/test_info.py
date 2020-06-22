import pytest

pytestmark = [pytest.mark.asyncio]


@pytest.fixture
def device():
    return {
        "id": "dd8475c9-80b8-472a-a7ba-c5aeff36fb9d",
        "online": True,
        "name": "Manjaro-Desktop",
        "domain": "mirumon.dev",
        "last_user": {
            "name": "nick",
            "fullname": "Nick Khitrov",
            "domain": "mirumon.dev",
        },
    }


@pytest.fixture
def device2():
    return {
        "id": "8f27dd84-5547-4873-bb80-3e59e5717546",
        "online": False,
        "name": "RED-DESKTOP",
        "domain": "mirumon.dev",
        "last_user": {
            "name": "aredruss",
            "fullname": "Alexander Medyanik",
            "domain": "mirumon.dev",
        },
    }


async def test_devices_list_without_registered_devices(
    app, client, token_header
) -> None:
    url = app.url_path_for(name="devices:list")
    response = await client.get(url, headers=token_header)
    assert response.json() == []
    assert response.status_code == 200


async def test_devices_list_with_two_devices(client, token_header, device, device2):
    url = client.application.url_path_for(name="devices:list")
    response = await client.get(url, headers=token_header)
    assert response.json() == [device, device2]
    assert response.status_code == 200


async def test_device_detail_event():
    pass


async def test_device_not_found():
    pass
