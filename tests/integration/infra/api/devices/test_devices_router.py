import uuid

import pytest

# TODO: add tests for permissions

pytestmark = [pytest.mark.asyncio]


@pytest.mark.parametrize(
    "url_name,method",
    [
        ("devices:detail", "get"),
        ("devices:software", "get"),
        ("devices:hardware", "get"),
        ("devices:shutdown", "post"),
        ("devices:execute", "post"),
    ],
)
async def test_device_not_found(app, client, url_name, method):
    call = {"get": client.get, "post": client.post}[method]

    url = app.url_path_for(url_name, device_id=str(uuid.uuid4()))
    response = await call(url)
    assert response.status_code == 404
    assert response.json() == {"detail": "device not found"}
