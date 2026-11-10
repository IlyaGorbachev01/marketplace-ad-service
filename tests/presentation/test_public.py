from httpx import AsyncClient


async def _create_ad(
    client: AsyncClient,
    auth_headers: dict[str, str],
    *,
    title: str = "MacBook Pro",
    price: int = 120000,
    category: str = "Электроника",
    city: str = "Москва",
) -> dict:
    resp = await client.post(
        "/ads",
        headers=auth_headers,
        json={
            "title": title,
            "description": "Описание",
            "price": price,
            "category": category,
            "city": city,
        },
    )
    assert resp.status_code == 201
    return resp.json()


async def test_create_ad_requires_auth(client: AsyncClient) -> None:
    resp = await client.post(
        "/ads",
        json={
            "title": "T",
            "description": "d",
            "price": 100,
            "category": "c",
            "city": "x",
        },
    )
    assert resp.status_code == 401


async def test_create_and_get_ad(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    created = await _create_ad(client, auth_headers)

    resp = await client.get(f"/ads/{created['id']}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "MacBook Pro"
    assert data["user_id"] == 1
    assert data["user_name"] == "Alice"
    assert data["views"] == 1

    resp = await client.get(f"/ads/{created['id']}")
    assert resp.status_code == 200
    assert resp.json()["views"] == 2


async def test_get_ad_not_found(client: AsyncClient) -> None:
    resp = await client.get("/ads/999")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Ad not found"


async def test_get_archived_ad_does_not_increment_views(
    client: AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    created = await _create_ad(client, auth_headers)
    await client.delete(f"/ads/{created['id']}", headers=auth_headers)

    resp = await client.get(f"/ads/{created['id']}")
    assert resp.status_code == 404

    internal = await client.get(f"/internal/ads/{created['id']}")
    assert internal.status_code == 200
    assert internal.json()["views"] == 0


async def test_list_ads_returns_all_active(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    await _create_ad(client, auth_headers, price=100, category="Электроника")
    await _create_ad(client, auth_headers, price=500, category="Электроника")
    await _create_ad(client, auth_headers, price=250, category="Одежда")

    resp = await client.get("/ads", params={"limit": 10, "offset": 0})
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 3
    assert len(data["items"]) == 3


async def test_list_my_ads_only_mine(
    client: AsyncClient,
    auth_headers: dict[str, str],
    other_auth_headers: dict[str, str],
) -> None:
    await _create_ad(client, auth_headers)
    await _create_ad(client, auth_headers)
    await _create_ad(client, other_auth_headers)

    resp = await client.get("/ads/my", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 2
    assert all(item["user_id"] == 1 for item in data["items"])


async def test_my_ads_requires_auth(client: AsyncClient) -> None:
    resp = await client.get("/ads/my")
    assert resp.status_code == 401


async def test_update_ad_by_author(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    created = await _create_ad(client, auth_headers)

    resp = await client.put(
        f"/ads/{created['id']}",
        headers=auth_headers,
        json={"price": 99999},
    )
    assert resp.status_code == 200
    assert resp.json()["price"] == 99999


async def test_update_ad_forbidden_for_non_author(
    client: AsyncClient,
    auth_headers: dict[str, str],
    other_auth_headers: dict[str, str],
) -> None:
    created = await _create_ad(client, auth_headers)

    resp = await client.put(
        f"/ads/{created['id']}",
        headers=other_auth_headers,
        json={"price": 1},
    )
    assert resp.status_code == 403
    assert resp.json()["detail"] == "Forbidden"


async def test_update_ad_not_found(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    resp = await client.put(
        "/ads/999",
        headers=auth_headers,
        json={"price": 1},
    )
    assert resp.status_code == 404


async def test_delete_ad_by_author(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    created = await _create_ad(client, auth_headers)

    resp = await client.delete(f"/ads/{created['id']}", headers=auth_headers)
    assert resp.status_code == 204

    resp = await client.get(f"/ads/{created['id']}")
    assert resp.status_code == 404


async def test_deleted_ad_hidden_from_my_ads(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    created = await _create_ad(client, auth_headers)
    await _create_ad(client, auth_headers)

    await client.delete(f"/ads/{created['id']}", headers=auth_headers)

    resp = await client.get("/ads/my", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert all(item["id"] != created["id"] for item in data["items"])


async def test_deleted_ad_hidden_from_list(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    created = await _create_ad(client, auth_headers)

    await client.delete(f"/ads/{created['id']}", headers=auth_headers)

    resp = await client.get("/ads")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 0


async def test_delete_ad_forbidden_for_non_author(
    client: AsyncClient,
    auth_headers: dict[str, str],
    other_auth_headers: dict[str, str],
) -> None:
    created = await _create_ad(client, auth_headers)

    resp = await client.delete(f"/ads/{created['id']}", headers=other_auth_headers)
    assert resp.status_code == 403


async def test_invalid_token_rejected(client: AsyncClient) -> None:
    resp = await client.post(
        "/ads",
        headers={"Authorization": "Bearer garbage"},
        json={
            "title": "T",
            "description": "d",
            "price": 100,
            "category": "c",
            "city": "x",
        },
    )
    assert resp.status_code == 401
