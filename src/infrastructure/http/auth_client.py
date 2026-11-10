import logging
import urllib.parse

import httpx

from src.application.ports.user_profile import UserInfo, UserProfileService
from src.tracing import trace_headers

logger = logging.getLogger(__name__)


class AuthServiceUserProfileService(UserProfileService):
    def __init__(self, client: httpx.AsyncClient, base_url: str) -> None:
        self._client = client
        self._base_url = base_url

    async def user(self, user_id: int) -> UserInfo | None:
        url = urllib.parse.urljoin(self._base_url, f"internal/users/{user_id}")
        try:
            resp = await self._client.get(url, headers=trace_headers())
        except httpx.HTTPError as exc:
            logger.warning("failed to fetch user %s: %s", user_id, exc)
            return None
        if resp.status_code != 200:
            return None
        data = resp.json()
        return UserInfo(id=data["user_id"], name=data["name"])
