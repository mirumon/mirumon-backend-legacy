from starlette.datastructures import State
from starlette.requests import HTTPConnection


def get_state(conn: HTTPConnection) -> State:
    return conn.app.state
