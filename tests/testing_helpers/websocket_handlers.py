from threading import Thread
from typing import Any, Callable, List


def process_event(
    api_method: Callable,
    api_kwargs: dict,
    client_websockets: List[Any],
    response_payloads: List[Any],
):

    processes = []
    for client_websocket, response_payload in zip(client_websockets, response_payloads):
        process = Thread(
            target=_process_event_by_device,
            kwargs=dict(
                client_websocket=client_websocket, response_payload=response_payload
            ),
        )
        process.start()
        processes.append(process)

    response = api_method(**api_kwargs)

    for process in processes:
        process.join()
    return response


def _process_event_by_device(client_websocket: Any, response_payload: Any):
    request_payload = client_websocket.receive_json()
    sync_id = request_payload.get("sync_id")

    resp_payload = {"event_result": response_payload, "sync_id": sync_id}
    client_websocket.send_json(resp_payload)
