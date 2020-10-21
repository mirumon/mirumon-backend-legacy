import pytest

pytestmark = pytest.mark.asyncio


async def test_device_shutdown(app, client, device_factory):
    async with device_factory() as device:
        url = app.url_path_for("devices:shutdown", device_id=device.id)
        response = await client.post(url)
        assert response.status_code == 202
        assert response.text == ""
