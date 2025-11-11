import random

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.users.schemas import UserCreate, UserRead, UserUpdate
from app.users.services import UserService
from app.users.dependencies import get_user_service

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserRead)
async def create_user(
    payload: UserCreate,
    service: UserService = Depends(get_user_service)
):
    return await service.register_user(payload)


@router.post("/seed/{count}", response_model=list[UserRead])
async def seed_users(
    count: int,
    service: UserService = Depends(get_user_service)
):
    """Seed the database with `count` test users."""
    users = []
    for i in range(count):
        payload = UserCreate(
            username=f"user{i+1}",
            password="password123",   # simple default for seeding
            xp=random.randint(1, 100) * 10,
            frozen_days=0,
            streak=0,
        )
        try:
            user = await service.register_user(payload)
            users.append(user)
        except HTTPException:
            # skip duplicates, continue seeding
            continue
    return users


@router.get("/{user_id}", response_model=UserRead)
async def get_user(
    user_id: int,
    service: UserService = Depends(get_user_service)
):
    user = await service.find_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: int,
    payload: UserUpdate,
    service: UserService = Depends(get_user_service)
):
    user = await service.find_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return await service.update_user(user, payload)


@router.delete("/{user_id}", response_model=UserRead)
async def delete_user(
    user_id: int,
    service: UserService = Depends(get_user_service)
):
    user = await service.find_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return await service.delete_user(user)


@router.post("/{username}/checkin", response_model=UserRead)
async def checkin_user(
    username: str,
    service: UserService = Depends(get_user_service)
):
    """
    Daily check-in endpoint:
    - Updates streaks, XP, and frozen days.
    - Publishes leaderboard event to Redis.
    """
    return await service.checkin(username)


@router.post("/sync-redis")
async def sync_users_to_redis(
    service: UserService = Depends(get_user_service)
):
    """
    Sync all users to Redis for leaderboard rebuild.
    """
    count = await service.sync_all_users_to_redis()
    return {"message": f"{count} users synced to Redis"}
