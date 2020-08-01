import pytest
from async_asgi_testclient import TestClient
from fastapi import FastAPI


@pytest.mark.usefixtures("migrations")
class BaseTestDevice:
    """Test scenario for http request for one device."""

    url_name = None
    expected_status_code = 200
    expected_return_payload = None

    device_id = "baa81326-9953-4587-92ce-82bb1ca1373c"
    pytestmark = pytest.mark.asyncio

    @pytest.fixture
    async def client(self, app: FastAPI, token_header):
        async with TestClient(
            app, headers={**token_header, "Content-Type": "application/json"}
        ) as client:
            yield client

    @pytest.fixture
    async def response(self, app: FastAPI, client, device_factory):
        assert self.url_name, "set url_name for test class"
        async with device_factory(device_id=self.device_id) as device:
            url = app.url_path_for(self.url_name, device_id=device.id)
            response = await client.get(url)
            return response

    async def test_should_return_expected_status_code(self, response):
        assert response.status_code == self.expected_status_code

    async def test_should_return_expected_payload(self, response):
        assert response.json() == self.expected_return_payload
