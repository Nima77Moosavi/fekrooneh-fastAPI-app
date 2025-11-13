import pytest
from httpx import AsyncClient
import uuid


@pytest.mark.anyio
async def test_health_check(async_client: AsyncClient):
    response = await async_client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.anyio
async def test_create_user(async_client: AsyncClient):
    unique_username = f"testuser_{uuid.uuid4().hex[:6]}"
    user_data = {
        "username": unique_username,
        "password": "pass",
        "xp": 50
    }

    response = await async_client.post("/users/", json=user_data)
    assert response.status_code == 200, f"Unexpected response: {response.text}"

    data = response.json()
    assert data.get("username") == user_data["username"]
    assert data.get("xp") == user_data["xp"]
