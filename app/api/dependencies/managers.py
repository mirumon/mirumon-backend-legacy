from typing import Callable

from starlette.requests import Request
from starlette.websockets import WebSocket

from app.services.clients_manager import ClientsManager
from app.services.events_manager import EventsManager


def clients_manager_retriever(for_websocket: bool = False) -> Callable:
    return (
        _get_clients_manager_for_http  # type: ignore
        if not for_websocket
        else _get_clients_manager_for_websockets
    )


def events_manager_retriever(for_websocket: bool = False) -> Callable:
    return (
        _get_events_manager_for_http  # type: ignore
        if not for_websocket
        else _get_events_manager_for_websockets
    )


def _get_clients_manager_for_http(request: Request) -> ClientsManager:
    return request.app.state.clients_manager


def _get_clients_manager_for_websockets(request: WebSocket) -> ClientsManager:
    return request.app.state.clients_manager


def _get_events_manager_for_http(request: Request) -> EventsManager:
    return request.app.state.events_manager


def _get_events_manager_for_websockets(request: WebSocket) -> EventsManager:
    return request.app.state.events_manager
