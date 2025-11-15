import pytest
from httpx import AsyncClient
from app.users.repositories import UserRepository
from app.users.schemas import UserCreate, UserUpdate
import uuid


@pytest.mark.anyio
async def test_create_user(test_db_session):
    unique_username = f"testuser_{uuid.uuid4().hex[:6]}"
    repo = UserRepository(test_db_session)
    user_data = UserCreate(username=unique_username, password="pass", xp=50)

    user = await repo.create(user_data)
    assert user.id is not None
    assert user.username == unique_username
    assert user.xp == 50
