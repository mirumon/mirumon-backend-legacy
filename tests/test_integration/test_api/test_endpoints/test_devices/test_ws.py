# def test_event_invalid_payload(device_client) -> None:
#     device_client.websocket.send_json({"invalid": "payload"})
#     assert device_client.websocket.receive_json() == {
#         "error": {
#             "code": 400,
#             "message": [
#                 {
#                     "loc": ["error"],
#                     "msg": "must provide result or error",
#                     "type": "value_error",
#                 },
#                 {
#                     "loc": ["sync_id"],
#                     "msg": "field required",
#                     "type": "value_error.missing",
#                 },
#             ],
#         },
#         "result": None,
#     }
#
#
# async def test_required_event_fields(
#     app: FastAPI, client: httpx.AsyncClient, device_client, computer_details_payload
# ) -> None:
#     invalid_payload = dict(
#         result=computer_details_payload,
#         error={
#             "code": 1004,
#             "message": "test message",
#             "description": "something wrong",
#         },
#     )
#
#     response = await process_event(
#         api_method=client.get,
#         api_kwargs=dict(
#             url=app.url_path_for(name="events:detail", device_id=device_client.id),
#         ),
#         client_websockets=[device_client.websocket],
#         response_payloads=[invalid_payload],
#     )
#
#     assert response.status_code == 503
#     assert response.json() == {"detail": "event is not supported by device"}
#
#     assert device_client.websocket.receive_json() == {
#         "error": {
#             "code": 400,
#             "message": [
#                 {
#                     "loc": ["error"],
#                     "msg": "must not provide both result and error",
#                     "type": "value_error",
#                 },
#             ],
#         },
#         "result": None,
#     }
#
#
# async def test_error_response_from_device(
#     app: FastAPI, client: httpx.AsyncClient, device_client
# ) -> None:
#     invalid_payload = dict(
#         error={
#             "code": 1004,
#             "message": "test message",
#             "description": "something wrong",
#         },
#     )
#
#     response = await process_event(
#         api_method=client.get,
#         api_kwargs=dict(
#             url=app.url_path_for(name="events:detail", device_id=device_client.id),
#         ),
#         client_websockets=[device_client.websocket],
#         response_payloads=[invalid_payload],
#     )
#
#     assert response.status_code == 503
#     assert response.json() == {"detail": {"code": 1004, "message": "test message"}}
#
# def test_unregistered_event(
#     app: FastAPI, test_client: TestClient, device_client, computer_details_payload,
# ):
#     device_client.websocket.send_json(
#         {"result": computer_details_payload, "sync_id": str(uuid.uuid4())},
#     )
#     assert device_client.websocket.receive_json() == {
#         "error": {"code": 404, "message": "'unregistered event'"},
#         "result": None,
#     }
