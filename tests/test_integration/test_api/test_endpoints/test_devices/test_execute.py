import pytest

pytestmark = pytest.mark.asyncio


async def test_device_execute(app, client, device_factory):
    async with device_factory() as device:
        url = app.url_path_for("devices:execute", device_id=device.id)
        payload = {"command": "ls", "args": ["-la"]}
        response = await client.post(url, json=payload)
        assert response.status_code == 202
        assert response.text == ""
