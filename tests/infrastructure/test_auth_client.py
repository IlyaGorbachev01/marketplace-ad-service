import httpx

from src.application.ports.user_profile import UserInfo
from src.infrastructure.http.auth_client import AuthServiceUserProfileService
from src.tracing import TRACE_HEADER, trace_scope


async def test_user_request_carries_trace_id() -> None:
    captured: dict[str, str] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["trace_id"] = request.headers.get(TRACE_HEADER, "")
        return httpx.Response(200, json={"user_id": 7, "name": "Alice"})

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as client:
        service = AuthServiceUserProfileService(client, "http://auth")
        with trace_scope("trace-7"):
            info = await service.user(7)

    assert info == UserInfo(id=7, name="Alice")
    assert captured["trace_id"] == "trace-7"


async def test_user_request_without_scope_has_no_trace_header() -> None:
    captured: dict[str, str] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["trace_id"] = request.headers.get(TRACE_HEADER, "")
        return httpx.Response(200, json={"user_id": 7, "name": "Alice"})

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as client:
        service = AuthServiceUserProfileService(client, "http://auth")
        await service.user(7)

    assert captured["trace_id"] == ""
