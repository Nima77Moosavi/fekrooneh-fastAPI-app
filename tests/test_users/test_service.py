import pytest
from app.users.repositories import UserRepository
from app.users.services import UserService
from app.users.schemas import UserCreate, UserUpdate


@pytest.mark.anyio
async def test_register_user_success(test_db_session):
    repo = UserRepository(test_db_session)
    service = UserService(repo)
    user_data = UserCreate(username="user", password="pass", xp=10)
    user = await service.register_user(user_data)
    assert user.id is not None
    assert user.username == "user"
    assert user.xp == 10
    
@pytest.mark.anyio
async def test_register_user_duplicate_username(test_db_session):
    repo = UserRepository(test_db_session)
    service = UserService(repo)
    user_data = UserCreate(username="duplicateuser", password="pass", xp=20)
    await service.register_user(user_data)
    with pytest.raises(Exception) as exc_info:
        await service.register_user(user_data)
    assert "Username already exists" in str(exc_info.value)    
    
@pytest.mark.anyio
async def test_find_user_by_id(test_db_session):
    repo = UserRepository(test_db_session)
    service = UserService(repo)
    user_data = UserCreate(username="findbyiduser", password="pass", xp=30)
    created_user = await service.register_user(user_data)
    fetched_user = await service.find_user_by_id(created_user.id)
    assert fetched_user.id == created_user.id
    assert fetched_user.username == created_user.username
    assert fetched_user.xp == created_user.xp
    
@pytest.mark.anyio
async def test_find_user_by_id_not_found(test_db_session):
    repo = UserRepository(test_db_session)
    service = UserService(repo)
    fetched_user = await service.find_user_by_id(9999)
    assert fetched_user is None
    
@pytest.mark.anyio
async def test_find_user_by_username(test_db_session):
    repo = UserRepository(test_db_session)
    service = UserService(repo)
    user_data = UserCreate(username="findbyusername", password="pass", xp=40)
    created_user = await service.register_user(user_data)
    fetched_user = await service.find_user_by_username("findbyusername")
    assert fetched_user.id == created_user.id
    
@pytest.mark.anyio
async def test_find_user_by_username_not_found(test_db_session):
    repo = UserRepository(test_db_session)
    service = UserService(repo)
    fetched_user = await service.find_user_by_username("nonexistentuser")
    assert fetched_user is None
    
@pytest.mark.anyio
async def test_update_user_xp(test_db_session):
    repo = UserRepository(test_db_session)
    service = UserService(repo)
    user_data = UserCreate(username="updateuser", password="pass", xp=50)
    created_user = await service.register_user(user_data)
    # Update user xp
    update_data = UserUpdate(xp=150)
    updated_user = await repo.update(created_user, update_data)
    assert updated_user.xp == 150
    
@pytest.mark.anyio
async def test_delete_user(test_db_session):
    repo = UserRepository(test_db_session)
    service = UserService(repo)
    user_data = UserCreate(username="deleteuser", password="pass", xp=60)
    created_user = await service.register_user(user_data)
    deleted_user = await service.delete_user(created_user)
    assert deleted_user.id == created_user.id
    # Verify user is deleted
    fetched_user = await service.find_user_by_id(created_user.id)
    assert fetched_user is None
    
@pytest.mark.anyio
async def test_delete_all_users(test_db_session):
    repo = UserRepository(test_db_session)
    service = UserService(repo)
    # Create multiple users
    users_data = [
        UserCreate(username=f"delalluser{i}", password="pass", xp=i*10) for i in range(3)
    ]
    for user_data in users_data:
        await service.register_user(user_data)
    deleted_count = await service.delete_all_users()
    # Verify all users are deleted
    all_users = await repo.list_all()
    assert len(all_users) == 0