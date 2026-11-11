from starlette.websockets import WebSocketDisconnect

from core.security import create_access_token
from core.ws_auth import authorize_ws_user


def make_websocket(token=None, origin="http://testserver", host="testserver"):
    headers = [(b"host", host.encode())]
    if origin is not None:
        headers.append((b"origin", origin.encode()))

    cookies = {}
    if token:
        cookies["access_token"] = token

    scope = {
        "type": "websocket",
        "asgi": {"version": "3.0"},
        "scheme": "ws",
        "path": "/ws/fyp_chat/5/student/201",
        "raw_path": b"/ws/fyp_chat/5/student/201",
        "query_string": b"",
        "headers": headers,
        "client": ("testclient", 50000),
        "server": ("testserver", 80),
        "subprotocols": [],
    }

    websocket = object.__new__(type("FakeWebSocket", (), {}))
    websocket.scope = scope
    websocket.headers = {
        "host": host,
        **({"origin": origin} if origin else {}),
    }
    websocket.cookies = cookies
    return websocket


def test_websocket_rejects_missing_token():
    websocket = make_websocket()

    assert authorize_ws_user(websocket, 5, "student", 201) is None


def test_websocket_rejects_wrong_url_user_id():
    token = create_access_token({
        "user_id": 100,
        "role": "student",
        "student_id": 201,
    })
    websocket = make_websocket(token)

    assert authorize_ws_user(websocket, 5, "student", 999) is None


def test_websocket_rejects_role_mismatch():
    token = create_access_token({
        "user_id": 100,
        "role": "student",
        "student_id": 201,
    })
    websocket = make_websocket(token)

    assert authorize_ws_user(websocket, 5, "teacher", 201) is None


def test_websocket_rejects_untrusted_origin():
    token = create_access_token({
        "user_id": 100,
        "role": "student",
        "student_id": 201,
    })
    websocket = make_websocket(token, origin="https://attacker.example")

    assert authorize_ws_user(websocket, 5, "student", 201) is None