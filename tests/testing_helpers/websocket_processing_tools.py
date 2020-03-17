from collections import namedtuple
from threading import Thread
from typing import Any, Callable, List

DeviceClient = namedtuple("DeviceClient", ["websocket", "uid"])


async def process_event(
        api_method: Callable,
        api_kwargs: dict,
        client_websockets: List[Any],
        response_payloads: List[Any],
):
    processes = []
    for client_websocket, response_payload in zip(client_websockets, response_payloads):
        process = Thread(
            target=process_event_by_device,
            kwargs=dict(
                client_websocket=client_websocket, response_payload=response_payload
            ),
        )
        process.start()
        processes.append(process)

    response = await api_method(**api_kwargs)

    for process in processes:
        process.join()
    return response


def process_event_by_device(client_websocket: Any, response_payload: dict):
    request_payload = client_websocket.receive_json()
    sync_id = request_payload["sync_id"]

    response_payload["sync_id"] = sync_id
    client_websocket.send_json(response_payload)
