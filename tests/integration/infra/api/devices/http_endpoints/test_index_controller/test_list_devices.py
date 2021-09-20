import uuid

import pytest

from mirumon.domain.devices.entities import Device

pytestmark = [pytest.mark.asyncio]


async def test_devices_list_without_registered_devices(app, client):
    url = app.url_path_for("devices:list")
    response = await client.get(url)
    assert response.status_code == 200
    assert response.json() == []


async def test_list_with_one_offline_device(app, client, devices_repo) -> None:
    device_id = uuid.uuid4()
    await devices_repo.create(Device(id=device_id, name="nick-laptop", properties={}))

    expected_device = {
        "id": str(device_id),
        "online": False,
        "name": "nick-laptop",
    }

    url = app.url_path_for("devices:list")
    response = await client.get(url)
    items = response.json()

    assert response.status_code == 200
    assert [expected_device] == items


async def test_list_with_two_offline_device(app, client, devices_repo) -> None:
    device_id = uuid.uuid4()
    device_id2 = uuid.uuid4()

    await devices_repo.create(Device(id=device_id, name="my device 1", properties={}))
    await devices_repo.create(Device(id=device_id2, name="my device 2", properties={}))

    expected_device = {
        "id": str(device_id),
        "online": False,
        "name": "my device 1",
    }
    expected_device2 = {
        "id": str(device_id2),
        "online": False,
        "name": "my device 2",
    }

    url = app.url_path_for("devices:list")
    response = await client.get(url)
    items = response.json()

    assert response.status_code == 200
    assert [expected_device, expected_device2] == items


async def test_list_with_one_online_device_and_one_offline_device(
    app, client, devices_repo, device_factory
) -> None:
    online_device_id = uuid.uuid4()
    offline_device_id = uuid.uuid4()

    await devices_repo.create(
        Device(id=offline_device_id, name="laptop", properties={})
    )

    expected_online_device = {
        "id": str(online_device_id),
        "online": True,
        "name": "desktop",
    }
    expected_offline_device = {
        "id": str(offline_device_id),
        "online": False,
        "name": "laptop",
    }
    async with device_factory(
        device_id=online_device_id, name=expected_online_device["name"]
    ):
        url = app.url_path_for("devices:list")
        response = await client.get(url)
        items = response.json()

        assert response.status_code == 200
        assert [expected_offline_device, expected_online_device] == items


async def test_list_with_one_online_device_only(app, client, device_factory) -> None:
    online_device_id = uuid.uuid4()
    expected_online_device = {
        "id": str(online_device_id),
        "online": True,
        "name": f"Device-{online_device_id}",
    }

    async with device_factory(device_id=online_device_id):
        url = app.url_path_for("devices:list")
        response = await client.get(url)
        items = response.json()

        assert response.status_code == 200
        assert [expected_online_device] == items


async def test_list_with_two_online_device_and_one_offline_device(
    app, client, devices_repo, device_factory
) -> None:
    online_device_id = uuid.uuid4()
    online_device_id2 = uuid.uuid4()
    offline_device_id = uuid.uuid4()

    await devices_repo.create(
        Device(id=offline_device_id, name="old pc", properties={})
    )
    expected_online_device = {
        "id": str(online_device_id),
        "online": True,
        "name": f"Device-{online_device_id}",
    }
    expected_online_device2 = {
        "id": str(online_device_id2),
        "online": True,
        "name": f"Device-{online_device_id2}",
    }
    expected_offline_device = {
        "id": str(offline_device_id),
        "online": False,
        "name": "old pc",
    }
    async with device_factory(device_id=online_device_id):
        async with device_factory(device_id=online_device_id2):
            url = app.url_path_for("devices:list")
            response = await client.get(url)
            items = response.json()

            assert response.status_code == 200

            assert [
                expected_offline_device,
                expected_online_device,
                expected_online_device2,
            ] == items
