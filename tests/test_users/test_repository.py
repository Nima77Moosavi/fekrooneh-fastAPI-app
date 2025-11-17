import pytest
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


@pytest.mark.anyio
async def test_get_user_by_id(test_db_session):
    repo = UserRepository(test_db_session)
    user_data = UserCreate(username="test", password="test", xp=10)
    created_user = await repo.create(user_data)
    fetched_user = await repo.get_by_id(created_user.id)
    assert fetched_user.id == created_user.id
    assert fetched_user.username == created_user.username
    assert fetched_user.xp == created_user.xp
    
@pytest.mark.anyio
async def test_get_by_username(test_db_session):
    repo = UserRepository(test_db_session)
    user_data = UserCreate(username="uniqueuser", password="test", xp=20)
    created_user = await repo.create(user_data)
    fetched_user = await repo.get_by_username("uniqueuser")
    assert fetched_user.id == created_user.id
    assert fetched_user.username == created_user.username
    assert fetched_user.xp == created_user.xp
    
@pytest.mark.anyio
async def test_list_all_users(test_db_session):
    repo = UserRepository(test_db_session)
    # Clear existing users
    await repo.delete_all()
    # Create multiple users
    users_data = [
        UserCreate(username=f"user{i}", password="pass", xp=i*10) for i in range(5)
    ]
    for user_data in users_data:
        await repo.create(user_data)
    all_users = await repo.list_all()
    assert len(all_users) == 5
    
@pytest.mark.anyio
async def test_update_user(test_db_session):
    repo = UserRepository(test_db_session)
    user_data = UserCreate(username="updatableuser", password="test", xp=30)
    created_user = await repo.create(user_data)
    update_data = UserUpdate(xp=100)
    updated_user = await repo.update(created_user, update_data)
    assert updated_user.xp == 100

@pytest.mark.anyio
async def test_delete_user(test_db_session):
    repo = UserRepository(test_db_session)
    user_data = UserCreate(username="deletableuser", password="test", xp=10)
    created_user = await repo.create(user_data)
    deleted_user = await repo.delete(created_user)
    assert deleted_user.id == created_user.id
    # Verify user is deleted
    fetched_user = await repo.get_by_id(created_user.id)
    assert fetched_user is None
    
@pytest.mark.anyio
async def test_delete_all_users(test_db_session):
    repo = UserRepository(test_db_session)
    # Create multiple users
    users_data = [
        UserCreate(username=f"userdel{i}", password="pass", xp=i*10) for i in range(3)
    ]
    for user_data in users_data:
        await repo.create(user_data)
    all_users = await repo.list_all()
    users_count = len(all_users)
    deleted_count = await repo.delete_all()
    assert deleted_count == users_count
    all_users = await repo.list_all()
    assert len(all_users) == 0