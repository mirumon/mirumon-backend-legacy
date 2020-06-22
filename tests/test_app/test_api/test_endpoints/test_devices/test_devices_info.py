import pytest
from fastapi import FastAPI

pytestmark = [pytest.mark.asyncio, pytest.mark.skip, pytest.mark.slow]


async def test_empty_devices_list_event(client, app: FastAPI) -> None:
    url = app.url_path_for(name="events:list")
    response = await client.get(url)
    assert response.status_code == 200
    assert response.json() == []


async def test_devices_list_event():
    pass


async def test_devices_list_with_disconnection(app: FastAPI, client) -> None:
    pass
    # def ws_disconnect(ws: Any) -> None:
    #     sleep(1)
    #     ws.close()
    #
    # client1, client2 = await new_clients(2)
    #
    # bad_process = Thread(target=ws_disconnect, kwargs=dict(ws=client1.websocket))
    #
    # process = Thread(
    #     target=process_event_by_device,
    #     kwargs=dict(
    #         client_websocket=client2.websocket,
    #         response_payload={"result": computer_inlist_payload},
    #     ),
    # )
    # bad_process.start()
    # process.start()
    #
    api_url = app.url_path_for("devices:list")
    response = await client.get(api_url)

    assert response.status_code == 200
    assert response.json() == []


async def test_device_detail_event():
    pass


async def test_device_not_found():
    pass


async def test_device_disconnection_in_detail_event_no_db():
    pass


async def test_device_disconnection_in_detail_event_with_db():
    pass


async def test_event_timeout_response_error():
    pass


async def test_event_validation_error():
    # todo parametrize events
    pass


async def test_validate_event_without_required_fields():
    pass
