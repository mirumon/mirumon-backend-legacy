import pprint
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
    system_info = {
        "name": "nick-laptop",
        "domain": "mirumon.dev",
        "workgroup": None,
        "last_user": {
            "name": "nick",
            "fullname": "Nick Khitrov",
            "domain": "mirumon.dev",
        },
        "os": [
            {
                "name": "Windows 10 Edu",
                "version": "1.12.12",
                "os_architecture": "amd64",
                "serial_number": "AGFNE-34GS-RYHRE",
                "number_of_users": 2,
            },
        ],
    }
    properties = {"system_info": system_info}
    await devices_repo.create(Device(id=device_id, properties=properties))

    expected_device = {
        "id": str(device_id),
        "online": False,
        "name": "nick-laptop",
        "domain": "mirumon.dev",
        "workgroup": None,
        "last_user": {
            "name": "nick",
            "fullname": "Nick Khitrov",
            "domain": "mirumon.dev",
        },
        "os": [
            {
                "name": "Windows 10 Edu",
                "version": "1.12.12",
                "os_architecture": "amd64",
                "serial_number": "AGFNE-34GS-RYHRE",
                "number_of_users": 2,
            },
        ],
    }

    url = app.url_path_for("devices:list")
    response = await client.get(url)
    items = response.json()

    assert response.status_code == 200
    assert [expected_device] == items


async def test_list_with_two_offline_device(app, client, devices_repo) -> None:
    device_id = uuid.uuid4()
    device_id2 = uuid.uuid4()

    system_info = {
        "name": "nick-desktop",
        "domain": "mirumon.dev",
        "workgroup": None,
        "last_user": {
            "name": "nick",
            "fullname": "Nick Khitrov",
            "domain": "mirumon.dev",
        },
        "os": [
            {
                "name": "Windows 10",
                "version": "1.12.12",
                "os_architecture": "amd64",
                "serial_number": "AGFNE-34GS-RYHRE",
                "number_of_users": 2,
            },
        ],
    }
    system_info2 = {
        "name": "nick-desktop",
        "domain": "mirumon.dev",
        "workgroup": None,
        "last_user": {
            "name": "nick",
            "fullname": "Nick Khitrov",
            "domain": "ad.mirumon.dev",
        },
        "os": [
            {
                "name": "Windows 10",
                "version": "1.12.12",
                "os_architecture": "amd64",
                "serial_number": "AGFNE-34GS-RYHRE",
                "number_of_users": 2,
            },
        ],
    }

    await devices_repo.create(
        Device(id=device_id, properties={"system_info": system_info})
    )
    await devices_repo.create(
        Device(id=device_id2, properties={"system_info": system_info2})
    )

    expected_device = {
        "id": str(device_id),
        "online": False,
        "name": "nick-desktop",
        "domain": "mirumon.dev",
        "workgroup": None,
        "last_user": {
            "name": "nick",
            "fullname": "Nick Khitrov",
            "domain": "mirumon.dev",
        },
        "os": [
            {
                "name": "Windows 10",
                "version": "1.12.12",
                "os_architecture": "amd64",
                "serial_number": "AGFNE-34GS-RYHRE",
                "number_of_users": 2,
            },
        ],
    }
    expected_device2 = {
        "id": str(device_id2),
        "online": False,
        "name": "nick-desktop",
        "domain": "mirumon.dev",
        "workgroup": None,
        "last_user": {
            "name": "nick",
            "fullname": "Nick Khitrov",
            "domain": "ad.mirumon.dev",
        },
        "os": [
            {
                "name": "Windows 10",
                "version": "1.12.12",
                "os_architecture": "amd64",
                "serial_number": "AGFNE-34GS-RYHRE",
                "number_of_users": 2,
            },
        ],
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

    system_info = {
        "name": "nick-laptop",
        "domain": "mirumon.dev",
        "workgroup": None,
        "last_user": {
            "name": "nick",
            "fullname": "Nick Khitrov",
            "domain": "mirumon.dev",
        },
        "os": [
            {
                "name": "Windows 10 Edu",
                "version": "1.12.12",
                "os_architecture": "amd64",
                "serial_number": "AGFNE-34GS-RYHRE",
                "number_of_users": 2,
            },
        ],
    }
    await devices_repo.create(
        Device(id=offline_device_id, properties={"system_info": system_info})
    )

    expected_online_device = {
        "id": str(online_device_id),
        "online": True,
        "name": "Manjaro-Desktop",
        "domain": "mirumon.dev",
        "workgroup": None,
        "last_user": {
            "name": "nick",
            "fullname": "Nick Khitrov",
            "domain": "mirumon.dev",
        },
        "os": [
            {
                "name": "Windows 10 Edu",
                "version": "1.12.12",
                "os_architecture": "amd64",
                "serial_number": "AGFNE-34GS-RYHRE",
                "number_of_users": 4,
            },
        ],
    }
    expected_offline_device = {
        "id": str(offline_device_id),
        "online": False,
        "name": "nick-laptop",
        "domain": "mirumon.dev",
        "workgroup": None,
        "last_user": {
            "name": "nick",
            "fullname": "Nick Khitrov",
            "domain": "mirumon.dev",
        },
        "os": [
            {
                "name": "Windows 10 Edu",
                "version": "1.12.12",
                "os_architecture": "amd64",
                "serial_number": "AGFNE-34GS-RYHRE",
                "number_of_users": 2,
            },
        ],
    }
    async with device_factory(device_id=online_device_id):
        url = app.url_path_for("devices:list")
        response = await client.get(url)
        items = response.json()

        assert response.status_code == 200
        assert [expected_online_device, expected_offline_device] == items


async def test_list_with_one_online_device_only(
    app, client, device_factory
) -> None:
    online_device_id = uuid.uuid4()
    expected_online_device = {
        "id": str(online_device_id),
        "online": True,
        "name": "Manjaro-Desktop",
        "domain": "mirumon.dev",
        "workgroup": None,
        "last_user": {
            "name": "nick",
            "fullname": "Nick Khitrov",
            "domain": "mirumon.dev",
        },
        "os": [
            {
                "name": "Windows 10 Edu",
                "version": "1.12.12",
                "os_architecture": "amd64",
                "serial_number": "AGFNE-34GS-RYHRE",
                "number_of_users": 4,
            },
        ],
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

    system_info = {
        "name": "nick-laptop",
        "domain": "mirumon.dev",
        "workgroup": None,
        "last_user": {
            "name": "nick",
            "fullname": "Nick Khitrov",
            "domain": "mirumon.dev",
        },
        "os": [
            {
                "name": "Windows 10 Edu",
                "version": "1.12.12",
                "os_architecture": "amd64",
                "serial_number": "AGFNE-34GS-RYHRE",
                "number_of_users": 2,
            },
        ],
    }
    await devices_repo.create(
        Device(id=offline_device_id, properties={"system_info": system_info})
    )

    expected_online_device = {
        "id": str(online_device_id),
        "online": True,
        "name": "Manjaro-Desktop",
        "domain": "mirumon.dev",
        "workgroup": None,
        "last_user": {
            "name": "nick",
            "fullname": "Nick Khitrov",
            "domain": "mirumon.dev",
        },
        "os": [
            {
                "name": "Windows 10 Edu",
                "version": "1.12.12",
                "os_architecture": "amd64",
                "serial_number": "AGFNE-34GS-RYHRE",
                "number_of_users": 4,
            },
        ],
    }
    expected_online_device2 = {
        "id": str(online_device_id2),
        "online": True,
        "name": "Manjaro-Desktop",
        "domain": "mirumon.dev",
        "workgroup": None,
        "last_user": {
            "name": "nick",
            "fullname": "Nick Khitrov",
            "domain": "mirumon.dev",
        },
        "os": [
            {
                "name": "Windows 10 Edu",
                "version": "1.12.12",
                "os_architecture": "amd64",
                "serial_number": "AGFNE-34GS-RYHRE",
                "number_of_users": 4,
            },
        ],
    }
    expected_offline_device = {
        "id": str(offline_device_id),
        "online": False,
        "name": "nick-laptop",
        "domain": "mirumon.dev",
        "workgroup": None,
        "last_user": {
            "name": "nick",
            "fullname": "Nick Khitrov",
            "domain": "mirumon.dev",
        },
        "os": [
            {
                "name": "Windows 10 Edu",
                "version": "1.12.12",
                "os_architecture": "amd64",
                "serial_number": "AGFNE-34GS-RYHRE",
                "number_of_users": 2,
            },
        ],
    }
    async with device_factory(device_id=online_device_id):
        async with device_factory(device_id=online_device_id2):
            url = app.url_path_for("devices:list")
            response = await client.get(url)
            items = response.json()

            assert response.status_code == 200
            print(1, online_device_id)
            print(2, online_device_id2)

            pprint.pprint({"response": items})
            assert [expected_online_device, expected_online_device2, expected_offline_device] == items

